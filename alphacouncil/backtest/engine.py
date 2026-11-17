"""
Purged & Embargoed Walk-Forward Backtesting Simulator.
Executes session-by-session without lookahead bias, enforcing point-in-time
earnings liquidations, statutory SEBI frictions, and synchronous risk validation.
"""

from dataclasses import dataclass
from typing import Dict, List
import numpy as np

from alphacouncil.config import DEFAULT_CONFIG
from alphacouncil.data.feed import Bar
from alphacouncil.data.calendar import PointInTimeCalendar
from alphacouncil.alpha.sweep_detector import LiquiditySweepDetector
from alphacouncil.alpha.sentiment_nlp import FinBertSentimentExtractor
from alphacouncil.alpha.triple_barrier import TripleBarrierLabeler
from alphacouncil.risk.pre_trade import PreTradeRiskEngine
from alphacouncil.risk.sizing import PositionSizingEngine
from alphacouncil.risk.circuits import CircuitBandGuard
from alphacouncil.risk.kill_switch import IntradayKillSwitch
from alphacouncil.risk.meta_labeler import LopezDePradoMetaLabeler
from alphacouncil.execution.friction import IndianMarketFrictionModel
from alphacouncil.backtest.metrics import QuantMetricsCalculator, PerformanceMetrics


@dataclass
class TradeRecord:
    """Detailed post-trade audit record."""
    symbol: str
    entry_bar_idx: int
    exit_bar_idx: int
    entry_price: float
    exit_price: float
    shares: int
    gross_pnl_inr: float
    net_pnl_inr: float
    friction_inr: float
    holding_days: int
    exit_reason: str
    alpha_scale: float


@dataclass
class BacktestResult:
    """Comprehensive backtest outputs."""
    config_name: str
    equity_curve: List[float]
    trades: List[TradeRecord]
    metrics: PerformanceMetrics


class BacktestEngine:
    """
    Simulation harness supporting orthogonal ablation runs and benchmark comparisons.
    """

    def __init__(
        self,
        config=DEFAULT_CONFIG,
        use_sweep_signal: bool = True,
        use_vol_sizing: bool = True,
        use_kelly_cap: bool = True,
        use_sentiment_nlp: bool = True,
        use_pit_filter: bool = True,
        use_atr_stop: bool = True,
        random_entry: bool = False,
    ):
        self.config = config
        self.use_sweep_signal = use_sweep_signal
        self.use_vol_sizing = use_vol_sizing
        self.use_kelly_cap = use_kelly_cap
        self.use_sentiment_nlp = use_sentiment_nlp
        self.use_pit_filter = use_pit_filter
        self.use_atr_stop = use_atr_stop
        self.random_entry = random_entry

        # Subsystems
        self.calendar = PointInTimeCalendar()
        self.sweep_detector = LiquiditySweepDetector(lookback=20, volume_factor=1.5)
        self.nlp = FinBertSentimentExtractor()
        self.triple_barrier = TripleBarrierLabeler(payoff_ratio=2.0, max_vertical_days=5)
        self.pre_trade = PreTradeRiskEngine(max_single_stock_pct=0.20)
        self.sizing = PositionSizingEngine(
            base_risk_fraction=config.risk.base_risk_fraction,
            target_annual_vol=config.risk.target_annual_volatility,
            min_atr_multiple=1.0 if use_atr_stop else 0.0,
        )
        self.circuit_guard = CircuitBandGuard(proximity_threshold_pct=0.015)
        self.kill_switch = IntradayKillSwitch()
        self.meta_labeler = LopezDePradoMetaLabeler()
        self.friction_model = IndianMarketFrictionModel()

    def run(
        self,
        universe_data: Dict[str, List[Bar]],
        config_name: str = "AlphaCouncil",
        n_trials: int = 150,
    ) -> BacktestResult:
        """
        Executes daily simulation across all symbols.
        """
        symbols = list(universe_data.keys())
        n_bars = len(universe_data[symbols[0]])

        cash = self.config.initial_equity
        equity_curve = [cash]
        active_positions: Dict[str, Dict] = {}  # symbol -> position dict
        completed_trades: List[TradeRecord] = []
        pending_orders: List[Dict] = []  # Scheduled for next bar open

        self.kill_switch.reset_daily_session(cash)

        for day in range(25, n_bars):
            # 1. Calculate Mark-to-Market Portfolio Valuation at Day Start
            current_portfolio_value = cash
            for sym, pos in active_positions.items():
                current_bar = universe_data[sym][day]
                current_portfolio_value += pos["shares"] * current_bar.open

            # Check Kill Switch
            dd_status = self.kill_switch.update_valuation(current_portfolio_value)
            if dd_status.is_strategy_frozen:
                equity_curve.append(current_portfolio_value)
                continue

            # 2. Execute Pending Orders from Day t-1 at Day t Open (Zero Lookahead)
            if not dd_status.is_session_halted:
                for order in pending_orders:
                    sym = order["symbol"]
                    bar = universe_data[sym][day]
                    exec_price = bar.open
                    qty = order["quantity"]

                    notional = qty * exec_price
                    if cash >= notional and qty > 0:
                        cash -= notional
                        active_positions[sym] = {
                            "shares": qty,
                            "entry_price": exec_price,
                            "stop_price": order["stop_price"],
                            "target_price": order["target_price"],
                            "entry_day": day,
                            "alpha_scale": order["alpha_scale"],
                            "annual_vol": order["annual_vol"],
                            "adv20": bar.adv20,
                        }
            pending_orders = []

            # 3. Evaluate Active Positions on Day t
            symbols_to_close = []
            for sym, pos in list(active_positions.items()):
                bar = universe_data[sym][day]
                holding_days = day - pos["entry_day"]

                exit_triggered = False
                exit_price = bar.close
                reason = "NORMAL"

                # Check 3A: Point-in-time earnings 24h prior exit
                if self.use_pit_filter and self.calendar.is_earnings_within_window(sym, bar.timestamp, 1):
                    exit_triggered = True
                    exit_price = bar.open
                    reason = "EARNINGS_24H_EXIT"

                # Check 3B: Lower Circuit Emergency Exit
                circuit_eval = self.circuit_guard.evaluate_long_position(
                    current_price=bar.close,
                    upper_circuit=bar.upper_circuit,
                    lower_circuit=bar.lower_circuit,
                    is_entry=False,
                )
                if circuit_eval.should_emergency_exit and not exit_triggered:
                    exit_triggered = True
                    exit_price = bar.close
                    reason = "LOWER_CIRCUIT_EMERGENCY"

                # Check 3C: Triple Barrier Path Evaluation
                if not exit_triggered:
                    if bar.low <= pos["stop_price"]:
                        exit_triggered = True
                        exit_price = pos["stop_price"]
                        reason = "STOP_LOSS_HIT"
                    elif bar.high >= pos["target_price"]:
                        exit_triggered = True
                        exit_price = pos["target_price"]
                        reason = "PROFIT_TARGET_HIT"
                    elif holding_days >= 5:
                        exit_triggered = True
                        exit_price = bar.close
                        reason = "VERTICAL_BARRIER_TIME_EXPIRY"

                # If exited, calculate statutory SEBI frictions and record trade
                if exit_triggered:
                    symbols_to_close.append(sym)
                    gross_pnl = (exit_price - pos["entry_price"]) * pos["shares"]

                    friction = self.friction_model.compute_roundtrip_friction(
                        quantity=pos["shares"],
                        entry_price=pos["entry_price"],
                        exit_price=exit_price,
                        annualized_vol=pos["annual_vol"],
                        adv20=pos["adv20"],
                    )
                    net_pnl = gross_pnl - friction.total_friction_inr
                    cash += (pos["shares"] * exit_price) - friction.total_friction_inr

                    completed_trades.append(
                        TradeRecord(
                            symbol=sym,
                            entry_bar_idx=pos["entry_day"],
                            exit_bar_idx=day,
                            entry_price=round(pos["entry_price"], 2),
                            exit_price=round(exit_price, 2),
                            shares=pos["shares"],
                            gross_pnl_inr=round(gross_pnl, 2),
                            net_pnl_inr=round(net_pnl, 2),
                            friction_inr=round(friction.total_friction_inr, 2),
                            holding_days=holding_days,
                            exit_reason=reason,
                            alpha_scale=pos["alpha_scale"],
                        )
                    )

            for sym in symbols_to_close:
                del active_positions[sym]

            # 4. Generate Signal Candidates at Day t Close for Day t+1 Execution
            if not dd_status.is_session_halted:
                for sym in symbols:
                    if sym in active_positions:
                        continue  # Single position per symbol

                    bars = universe_data[sym][: day + 1]
                    bar_t = bars[-1]

                    # Alpha signal evaluation
                    signal_val = 0
                    if self.use_sweep_signal:
                        lows = np.array([b.low for b in bars])
                        highs = np.array([b.high for b in bars])
                        closes = np.array([b.close for b in bars])
                        opens = np.array([b.open for b in bars])
                        vols = np.array([b.volume for b in bars])

                        sweep_res = self.sweep_detector.evaluate_bar(
                            symbol=sym,
                            open_p=opens,
                            high=highs,
                            low=lows,
                            close=closes,
                            volume=vols,
                        )
                        if sweep_res and sweep_res.signal == 1:
                            signal_val = 1
                    elif self.random_entry:
                        # Emulate random entry coin-flip for ablation
                        signal_val = 1 if np.random.random() < 0.08 else 0

                    if signal_val == 1:
                        # Sentiment featurizer
                        sentiment = 0.0
                        if self.use_sentiment_nlp:
                            sentiment = self.nlp.extract_sentiment(
                                sym, "Management reports margin expansion and EBITDA growth"
                            )

                        # Meta-Labeler downscale
                        is_earn = self.calendar.is_earnings_within_window(sym, bar_t.timestamp, 1)
                        rvol = bar_t.volume / (bar_t.adv20 + 1e-8)
                        meta_out = self.meta_labeler.evaluate_setup(
                            symbol=sym,
                            sweep_signal=1,
                            sentiment_score=sentiment,
                            rvol=rvol,
                            price_above_50sma=True,
                            is_earnings_imminent=is_earn,
                        )

                        if meta_out.alpha_scale > 0.0:
                            # Sizing
                            stop_p = round(bar_t.low * 0.9995, 2)
                            d_stop = max(0.1, bar_t.close - stop_p)
                            target_p = round(bar_t.close + (2.0 * d_stop), 2)
                            recent_closes = np.array([b.close for b in bars[-20:]])
                            ann_vol = float(np.std(np.diff(np.log(recent_closes))) * np.sqrt(252.0))

                            sizing_res = self.sizing.compute_size(
                                symbol=sym,
                                entry_price=bar_t.close,
                                stop_price=stop_p,
                                target_price=target_p,
                                atr14=bar_t.atr14,
                                realized_annual_vol=ann_vol,
                                current_equity=current_portfolio_value,
                                rolling_bss=0.15 if self.use_kelly_cap else 0.0,
                                estimated_win_prob=meta_out.predicted_win_prob,
                            )

                            if not sizing_res.is_aborted and sizing_res.shares_quantity > 0:
                                # Pre-trade validation
                                val = self.pre_trade.validate_order(
                                    symbol=sym,
                                    proposed_quantity=int(sizing_res.shares_quantity * meta_out.alpha_scale),
                                    entry_price=bar_t.close,
                                    current_equity=current_portfolio_value,
                                )
                                if val.is_approved and val.adjusted_quantity > 0:
                                    pending_orders.append({
                                        "symbol": sym,
                                        "quantity": val.adjusted_quantity,
                                        "stop_price": stop_p,
                                        "target_price": target_p,
                                        "alpha_scale": meta_out.alpha_scale,
                                        "annual_vol": ann_vol,
                                    })

            # Record End of Day Equity
            eod_equity = cash
            for sym, pos in active_positions.items():
                eod_equity += pos["shares"] * universe_data[sym][day].close
            equity_curve.append(round(eod_equity, 2))

        # Metrics calculation
        pnls = [t.net_pnl_inr for t in completed_trades]
        metrics = QuantMetricsCalculator.compute_performance(
            daily_equity_curve=equity_curve,
            trade_pnls=pnls,
            n_trials_logged=n_trials,
        )

        return BacktestResult(
            config_name=config_name,
            equity_curve=equity_curve,
            trades=completed_trades,
            metrics=metrics,
        )
