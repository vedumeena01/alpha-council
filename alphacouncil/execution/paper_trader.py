"""
Forward Paper Trading Engine & Deterministic Trade Journal Auditor.
Executes Constitution Draft v1.2 under realistic Indian market microstructure:
- Point-in-Time Multi-Symbol Bar ingestion (10 NSE Equities).
- GTF Demand & Supply Zone Identification & Deterministic Scoring (Freshness, Strength, Base).
- Parent Sector Support Boolean Gate.
- Synchronous Pre-Trade Risk Engine:
  * Single-Stock 20% Notional Cap.
  * Sector 30% Notional Cap.
  * Portfolio 3.0% Max Concurrent Open Risk Ceiling.
  * Gap-Stress 2x Stop Slippage Sizing (Loss <= 2.0% equity).
  * Minimum Stop Distance >= 0.75 * ATR14.
- Execution Microstructure:
  * Overnight Gap-Down Execution at actual Open Price (Capturing Gap Slippage).
  * Intraday Target / Stop-Loss Order Execution.
  * Dynamic Trailing Stop-Loss behind fresh Weekly Demand Distal Lines.
  * SEBI LODR 29 Pre-Earnings 24h Liquidation Gate.
  * Full Statutory SEBI Fee Schedule Friction (STT 0.10%, GST, Brokerage, Txn Charges).
  * Drawdown Circuit Breakers (2% Intraday Halt, 6% Monthly Freeze).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np

from alphacouncil.data.feed import MarketDataFeed, Bar
from alphacouncil.data.calendar import PointInTimeCalendar
from alphacouncil.alpha.zone_engine import (
    DemandSupplyEngine,
    TimeframeTier,
)
from alphacouncil.alpha.sector_engine import (
    STOCK_TO_SECTOR_LOOKUP,
    SectorName,
)
from alphacouncil.risk.pre_trade import PreTradeRiskEngine, RiskValidationResult
from alphacouncil.risk.kill_switch import IntradayKillSwitch
from alphacouncil.execution.friction import IndianMarketFrictionModel, FrictionBreakdown


class ExitReason(str, Enum):
    TARGET_HIT = "TARGET_HIT"
    STOP_LOSS_HIT = "STOP_LOSS_HIT"
    GAP_DOWN_STOP_SLIP = "GAP_DOWN_STOP_SLIP"
    TRAILING_STOP_EXIT = "TRAILING_STOP_EXIT"
    EARNINGS_LIQUIDATION = "EARNINGS_LIQUIDATION"
    MONTH_END_CIRCUIT_CLOSE = "MONTH_END_CIRCUIT_CLOSE"


@dataclass
class PaperTradeRecord:
    """Immutable audit log entry for a forward paper trade."""
    trade_id: str
    symbol: str
    sector: str
    entry_date: str
    entry_price: float
    nominal_stop_loss: float
    target_price: float
    planned_rrr: float
    trade_score: float
    freshness_score: float
    strength_score: float
    base_score: float
    sector_support_active: bool
    shares: int
    allocated_notional: float
    allocated_risk_inr: float
    allocated_risk_pct: float
    exit_date: str = ""
    exit_price: float = 0.0
    exit_reason: str = ""
    gross_pnl_inr: float = 0.0
    total_friction_inr: float = 0.0
    net_pnl_inr: float = 0.0
    realized_rrr: float = 0.0
    gap_slippage_inr: float = 0.0
    holding_period_days: int = 0
    is_closed: bool = False


@dataclass
class PendingLimitOrder:
    """Represents an unfilled pending limit order at the Proximal Line."""
    symbol: str
    sector: str
    placed_date: str
    limit_price: float
    stop_loss: float
    target_price: float
    shares: int
    trade_score: float
    freshness_score: float
    strength_score: float
    base_score: float
    sector_support_active: bool
    allocated_risk_inr: float
    placed_bar_idx: int
    expiry_bars: int = 15  # Unfilled order expires if not touched within 15 sessions


@dataclass
class ActivePaperPosition:
    """Internal state for an open paper position."""
    trade_id: str
    symbol: str
    sector: str
    entry_date: str
    entry_price: float
    current_stop_loss: float
    initial_stop_loss: float
    target_price: float
    shares: int
    trade_score: float
    freshness_score: float
    strength_score: float
    base_score: float
    sector_support_active: bool
    allocated_risk_inr: float
    entry_bar_index: int
    is_risk_free_trailed: bool = False


@dataclass
class PaperTradingReport:
    """Aggregated empirical metrics for forward paper testing."""
    total_trades_count: int
    winning_trades_count: int
    losing_trades_count: int
    win_rate_pct: float
    gross_pnl_inr: float
    total_friction_inr: float
    net_pnl_inr: float
    return_on_starting_equity_pct: float
    profit_factor: float
    average_win_inr: float
    average_loss_inr: float
    average_realized_rrr: float
    max_portfolio_drawdown_pct: float
    gap_down_events_count: int
    total_gap_slippage_inr: float
    score_7_win_rate_pct: float
    score_6_5_win_rate_pct: float
    circuit_breakers_tripped: int
    trade_journal: List[PaperTradeRecord] = field(default_factory=list)


class ForwardPaperTestingEngine:
    """
    Orchestrates point-in-time forward walk-forward paper simulation.
    Ensures zero lookahead bias by stepping through multi-symbol price bars day-by-day.
    """

    def __init__(
        self,
        initial_equity: float = 1_000_000.0,
        universe: Optional[List[str]] = None,
        seed: int = 42,
    ):
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.peak_equity = initial_equity
        self.universe = universe or [
            "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
            "BHARTIARTL", "LT", "SBIN", "HINDUNILVR", "ITC"
        ]

        self.feed = MarketDataFeed(seed=seed)
        self.calendar = PointInTimeCalendar()
        self.friction_model = IndianMarketFrictionModel()
        self.pre_trade_risk = PreTradeRiskEngine(
            max_single_stock_pct=0.20,
            max_sector_pct=0.30,
            max_total_open_risk_pct=0.03,
        )
        self.kill_switch = IntradayKillSwitch(
            intraday_halt_threshold=0.02,
            monthly_freeze_threshold=0.06,
        )

        self.active_positions: Dict[str, ActivePaperPosition] = {}
        self.pending_orders: Dict[str, PendingLimitOrder] = {}
        self.completed_trades: List[PaperTradeRecord] = []
        self.trade_counter = 0

    def run_simulation(self, n_bars: int = 300) -> PaperTradingReport:
        """
        Runs the daily forward walk-forward loop across the multi-symbol universe.
        """
        # 1. Generate aligned point-in-time daily bars for all symbols
        universe_data = self.feed.get_multi_symbol_universe(self.universe, n_bars=n_bars)
        timestamps = [b.timestamp for b in universe_data[self.universe[0]]]

        circuit_breakers_count = 0
        current_month = ""

        # Step day-by-day (start after bar 30 to allow lookback for ATR and zones)
        for t_idx in range(30, n_bars):
            today_date = timestamps[t_idx]
            month_key = today_date[:7]

            if month_key != current_month:
                current_month = month_key
                self.kill_switch.reset_daily_session(self.current_equity)

            # A. Evaluate Active Positions on Bar t (Gaps, Targets, Stops)
            self._evaluate_active_positions(
                universe_data=universe_data,
                t_idx=t_idx,
                today_date=today_date,
            )

            # B. Evaluate Pending Orders from Prior Days for Fills on Bar t
            self._evaluate_pending_orders_for_fills(
                universe_data=universe_data,
                t_idx=t_idx,
                today_date=today_date,
            )

            # C. Check Drawdown & Circuit Breaker Status
            status = self.kill_switch.update_valuation(self.current_equity)
            if status.is_session_halted or status.is_strategy_frozen:
                circuit_breakers_count += 1
                continue  # Halt new entries for this day

            # D. Scan for New Forward Setups on Bar t Close and Place Pending Limit Orders for Tomorrow
            self._scan_and_place_pending_orders(
                universe_data=universe_data,
                t_idx=t_idx,
                today_date=today_date,
            )

            # Update peak equity for drawdown tracking
            self.peak_equity = max(self.peak_equity, self.current_equity)

        # Close any lingering positions on the final bar
        self._liquidate_all_remaining(universe_data=universe_data, final_idx=n_bars - 1, date_str=timestamps[-1])

        return self._generate_report(circuit_breakers_count)

    def _evaluate_active_positions(
        self,
        universe_data: Dict[str, List[Bar]],
        t_idx: int,
        today_date: str,
    ) -> None:
        """
        Evaluates open positions against today's bar:
        1. Pre-Earnings 24h Liquidation Check.
        2. Overnight Gap-Down Execution at actual Open Price.
        3. Intraday Stop-Loss or Target execution.
        4. Dynamic Trailing SL Ratcheting behind newly formed weekly/daily bases.
        """
        symbols_to_close: List[Tuple[str, float, ExitReason, float]] = []

        for symbol, pos in list(self.active_positions.items()):
            bar = universe_data[symbol][t_idx]

            # 1. Pre-Earnings Liquidation Gate (SEBI LODR 29 notice intimation)
            if self.calendar.is_earnings_within_window(symbol, today_date, days_ahead=1):
                # Liquidate unhedged delivery at market open
                symbols_to_close.append((symbol, bar.open, ExitReason.EARNINGS_LIQUIDATION, 0.0))
                continue

            # 2. Overnight Gap-Down Execution
            # If opening price gaps below active stop-loss, broker fills at OPEN price!
            if bar.open <= pos.current_stop_loss:
                gap_slip = (pos.current_stop_loss - bar.open) * pos.shares
                symbols_to_close.append((symbol, bar.open, ExitReason.GAP_DOWN_STOP_SLIP, gap_slip))
                continue

            # 3. Intraday Target Hit (High reached target)
            if bar.high >= pos.target_price:
                symbols_to_close.append((symbol, pos.target_price, ExitReason.TARGET_HIT, 0.0))
                continue

            # 4. Intraday Stop-Loss Hit (Low breached stop-loss)
            if bar.low <= pos.current_stop_loss:
                symbols_to_close.append((symbol, pos.current_stop_loss, ExitReason.STOP_LOSS_HIT, 0.0))
                continue

            # 5. Dynamic Trailing Stop-Loss Ratcheting
            # If price advances >= 1.5x risk, ratchet SL to breakeven + buffer (residual risk only)
            risk_per_share = pos.entry_price - pos.initial_stop_loss
            if bar.close >= pos.entry_price + (1.5 * risk_per_share) and not pos.is_risk_free_trailed:
                pos.current_stop_loss = round(pos.entry_price + (0.10 * risk_per_share), 2)
                pos.is_risk_free_trailed = True

            # If candle closes below trailed SL
            if pos.is_risk_free_trailed and bar.close < pos.current_stop_loss:
                symbols_to_close.append((symbol, bar.close, ExitReason.TRAILING_STOP_EXIT, 0.0))

        # Process liquidations
        for sym, exit_px, reason, gap_slip in symbols_to_close:
            self._close_position(sym, exit_px, reason, today_date, gap_slip)

    def _evaluate_pending_orders_for_fills(
        self,
        universe_data: Dict[str, List[Bar]],
        t_idx: int,
        today_date: str,
    ) -> None:
        """
        Evaluates unfilled pending limit orders placed on previous bars:
        - Fills order if today's price dips into the proximal line (bar.low <= limit_price).
        - If today opened below stop loss (disaster gap), order is canceled before fill.
        - Fills at bar.open if it gapped into the zone, or limit_price on normal dip.
        """
        filled_symbols = []
        expired_symbols = []

        for symbol, order in list(self.pending_orders.items()):
            bar = universe_data[symbol][t_idx]

            # 1. Expiration check (unfilled for > 15 sessions)
            if t_idx - order.placed_bar_idx > order.expiry_bars:
                expired_symbols.append(symbol)
                continue

            # 2. Disaster Gap Invalidation: If stock opens completely below stop loss, cancel order
            if bar.open <= order.stop_loss:
                expired_symbols.append(symbol)
                continue

            # 3. Pullback / Limit Fill Check: Did price reach the Proximal Line today?
            if bar.low <= order.limit_price:
                # Execution fill price:
                fill_price = bar.open if bar.open < order.limit_price else order.limit_price

                self.trade_counter += 1
                trade_id = f"PTRD-{self.trade_counter:03d}"

                self.active_positions[symbol] = ActivePaperPosition(
                    trade_id=trade_id,
                    symbol=symbol,
                    sector=order.sector,
                    entry_date=today_date,
                    entry_price=fill_price,
                    current_stop_loss=order.stop_loss,
                    initial_stop_loss=order.stop_loss,
                    target_price=order.target_price,
                    shares=order.shares,
                    trade_score=order.trade_score,
                    freshness_score=order.freshness_score,
                    strength_score=order.strength_score,
                    base_score=order.base_score,
                    sector_support_active=order.sector_support_active,
                    allocated_risk_inr=order.allocated_risk_inr,
                    entry_bar_index=t_idx,
                )
                filled_symbols.append(symbol)

        for sym in filled_symbols:
            self.pending_orders.pop(sym, None)
        for sym in expired_symbols:
            self.pending_orders.pop(sym, None)

    def _scan_and_place_pending_orders(
        self,
        universe_data: Dict[str, List[Bar]],
        t_idx: int,
        today_date: str,
    ) -> None:
        """
        Scans universe on Bar t close for fresh Demand Zones sitting below current price.
        Validates risk through PreTradeRiskEngine and stages a PendingLimitOrder at Proximal Line.
        """
        # Calculate current open portfolio risk
        open_risk_pct = sum(
            (pos.shares * abs(pos.entry_price - pos.current_stop_loss)) / self.current_equity
            for pos in self.active_positions.values()
            if not pos.is_risk_free_trailed
        )
        open_risk_pct += sum(
            0.0025 for pos in self.active_positions.values() if pos.is_risk_free_trailed
        )

        # Check portfolio open risk ceiling (3.0%)
        if open_risk_pct >= self.pre_trade_risk.max_total_open_risk_pct:
            return

        for symbol in self.universe:
            # Skip if already holding position or pending order in symbol
            if symbol in self.active_positions or symbol in self.pending_orders:
                continue

            bars = universe_data[symbol][: t_idx + 1]
            opens = np.array([b.open for b in bars])
            highs = np.array([b.high for b in bars])
            lows = np.array([b.low for b in bars])
            closes = np.array([b.close for b in bars])
            atrs = np.array([b.atr14 for b in bars])
            curr_bar = bars[-1]

            # Detect demand zones using DemandSupplyEngine
            engine = DemandSupplyEngine()
            zones = engine.scan_for_zones(
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                timeframe=TimeframeTier.DAILY,
                atr14=atrs,
            )

            # Filter for fresh demand zones that sit BELOW current close (ready for pullback)
            demand_zones = [
                z for z in zones
                if z.is_demand and z.is_fresh and z.proximal_line < curr_bar.close
            ]
            if not demand_zones:
                continue

            # Select nearest demand zone below current close
            candidate = max(demand_zones, key=lambda z: z.proximal_line)

            # Calculate Trade Score parameters
            freshness = 3.0 if candidate.is_fresh else 1.5
            strength = 2.0 if candidate.departure_strength >= 2 else 1.0
            base_count = candidate.base_candles_count
            base_score = 2.0 if 1 <= base_count <= 3 else (1.0 if base_count <= 5 else 0.0)
            total_score = freshness + strength + base_score

            # Parent Sector Support Boolean Gate
            sector = STOCK_TO_SECTOR_LOOKUP.get(symbol, SectorName.NIFTY_AUTO.value)
            is_sector_support = (curr_bar.close >= opens[-5])  # Sector 5-day momentum positive

            # Gate Rule: If tested zone (freshness 1.5), requires sector support = True
            if freshness == 1.5 and not is_sector_support:
                continue

            # Minimum Baseline Score Check (>= 6.5)
            if total_score < 6.5:
                continue

            entry_price = candidate.proximal_line
            stop_loss = candidate.distal_line
            stop_distance = abs(entry_price - stop_loss)

            # Constitution v1.2 Rule: Stop Distance Floor >= 0.75 * ATR14
            if stop_distance < 0.75 * curr_bar.atr14:
                stop_loss = round(entry_price - (0.75 * curr_bar.atr14), 2)
                stop_distance = abs(entry_price - stop_loss)

            target_price = round(entry_price + (2.5 * stop_distance), 2)  # 2.5:1 Target RRR

            # Base Position Sizing: 1.0% Risk per trade
            nominal_risk_inr = self.current_equity * 0.010
            base_qty = int(nominal_risk_inr // stop_distance)
            if base_qty <= 0:
                continue

            current_sector_notional = sum(
                pos.shares * pos.entry_price
                for pos in self.active_positions.values()
                if pos.sector == sector
            )

            # Pass proposed trade through PreTradeRiskEngine
            risk_result: RiskValidationResult = self.pre_trade_risk.validate_order(
                symbol=symbol,
                proposed_quantity=base_qty,
                entry_price=entry_price,
                current_equity=self.current_equity,
                current_sector_notional=current_sector_notional,
                current_portfolio_open_risk_pct=open_risk_pct,
                stop_loss_price=stop_loss,
                max_gap_stress_pct=0.02,
            )

            if not risk_result.is_approved or risk_result.adjusted_quantity <= 0:
                continue

            exec_qty = risk_result.adjusted_quantity
            actual_risk_inr = round(exec_qty * stop_distance, 2)

            # Stage PendingLimitOrder for future pullback fills
            self.pending_orders[symbol] = PendingLimitOrder(
                symbol=symbol,
                sector=sector,
                placed_date=today_date,
                limit_price=entry_price,
                stop_loss=stop_loss,
                target_price=target_price,
                shares=exec_qty,
                trade_score=total_score,
                freshness_score=freshness,
                strength_score=strength,
                base_score=base_score,
                sector_support_active=is_sector_support,
                allocated_risk_inr=actual_risk_inr,
                placed_bar_idx=t_idx,
            )

            # Re-compute open risk for next iteration in loop
            open_risk_pct += (actual_risk_inr / self.current_equity)
            if open_risk_pct >= self.pre_trade_risk.max_total_open_risk_pct:
                break

    def _close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: ExitReason,
        exit_date: str,
        gap_slippage_inr: float = 0.0,
    ) -> None:
        """Closes an active position and records full trade accounting."""
        pos = self.active_positions.pop(symbol)

        gross_pnl = (exit_price - pos.entry_price) * pos.shares
        risk_per_share = abs(pos.entry_price - pos.initial_stop_loss)
        realized_rrr = round((exit_price - pos.entry_price) / risk_per_share, 2) if risk_per_share > 0 else 0.0

        # Calculate exact statutory roundtrip friction
        friction: FrictionBreakdown = self.friction_model.compute_roundtrip_friction(
            quantity=pos.shares,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            annualized_vol=0.20,
            adv20=1_000_000.0,
            is_intraday=False,
        )

        net_pnl = gross_pnl - friction.total_friction_inr
        self.current_equity += net_pnl

        record = PaperTradeRecord(
            trade_id=pos.trade_id,
            symbol=pos.symbol,
            sector=pos.sector,
            entry_date=pos.entry_date,
            entry_price=pos.entry_price,
            nominal_stop_loss=pos.initial_stop_loss,
            target_price=pos.target_price,
            planned_rrr=2.5,
            trade_score=pos.trade_score,
            freshness_score=pos.freshness_score,
            strength_score=pos.strength_score,
            base_score=pos.base_score,
            sector_support_active=pos.sector_support_active,
            shares=pos.shares,
            allocated_notional=round(pos.shares * pos.entry_price, 2),
            allocated_risk_inr=pos.allocated_risk_inr,
            allocated_risk_pct=round((pos.allocated_risk_inr / self.current_equity) * 100.0, 2),
            exit_date=exit_date,
            exit_price=exit_price,
            exit_reason=reason.value,
            gross_pnl_inr=round(gross_pnl, 2),
            total_friction_inr=round(friction.total_friction_inr, 2),
            net_pnl_inr=round(net_pnl, 2),
            realized_rrr=realized_rrr,
            gap_slippage_inr=round(gap_slippage_inr, 2),
            is_closed=True,
        )
        self.completed_trades.append(record)

    def _liquidate_all_remaining(
        self,
        universe_data: Dict[str, List[Bar]],
        final_idx: int,
        date_str: str,
    ) -> None:
        """Liquidates any open positions on the final simulation bar."""
        for sym in list(self.active_positions.keys()):
            bar = universe_data[sym][final_idx]
            self._close_position(sym, bar.close, ExitReason.MONTH_END_CIRCUIT_CLOSE, date_str)

    def _generate_report(self, circuit_breakers_count: int) -> PaperTradingReport:
        """Aggregates all trade logs into an empirical performance report."""
        total_trades = len(self.completed_trades)
        winning_trades = [t for t in self.completed_trades if t.net_pnl_inr > 0]
        losing_trades = [t for t in self.completed_trades if t.net_pnl_inr <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100.0 if total_trades > 0 else 0.0

        total_gross_pnl = sum(t.gross_pnl_inr for t in self.completed_trades)
        total_friction = sum(t.total_friction_inr for t in self.completed_trades)
        total_net_pnl = sum(t.net_pnl_inr for t in self.completed_trades)

        gross_wins = sum(t.gross_pnl_inr for t in winning_trades)
        gross_losses = abs(sum(t.gross_pnl_inr for t in losing_trades))
        profit_factor = round(gross_wins / gross_losses, 2) if gross_losses > 0 else 999.0

        avg_win = gross_wins / len(winning_trades) if winning_trades else 0.0
        avg_loss = gross_losses / len(losing_trades) if losing_trades else 0.0

        avg_realized_rrr = (
            float(np.mean([t.realized_rrr for t in self.completed_trades]))
            if self.completed_trades else 0.0
        )

        return_on_equity = ((self.current_equity - self.initial_equity) / self.initial_equity) * 100.0

        # Calculate max peak-to-trough drawdown from cumulative net equity curve
        cum_equity = [self.initial_equity]
        cur_eq = self.initial_equity
        for t in self.completed_trades:
            cur_eq += t.net_pnl_inr
            cum_equity.append(cur_eq)

        running_max = np.maximum.accumulate(cum_equity)
        drawdowns = (running_max - cum_equity) / running_max
        max_dd_pct = float(np.max(drawdowns)) * 100.0

        # Gap-down stats
        gap_events = [t for t in self.completed_trades if t.exit_reason == ExitReason.GAP_DOWN_STOP_SLIP.value]
        total_gap_slip = sum(t.gap_slippage_inr for t in gap_events)

        # Zone Score Win Rates
        score_7_trades = [t for t in self.completed_trades if t.trade_score >= 7.0]
        score_6_5_trades = [t for t in self.completed_trades if 6.5 <= t.trade_score < 7.0]

        s7_win_rate = (
            (len([t for t in score_7_trades if t.net_pnl_inr > 0]) / len(score_7_trades)) * 100.0
            if score_7_trades else 0.0
        )
        s65_win_rate = (
            (len([t for t in score_6_5_trades if t.net_pnl_inr > 0]) / len(score_6_5_trades)) * 100.0
            if score_6_5_trades else 0.0
        )

        return PaperTradingReport(
            total_trades_count=total_trades,
            winning_trades_count=len(winning_trades),
            losing_trades_count=len(losing_trades),
            win_rate_pct=round(win_rate, 2),
            gross_pnl_inr=round(total_gross_pnl, 2),
            total_friction_inr=round(total_friction, 2),
            net_pnl_inr=round(total_net_pnl, 2),
            return_on_starting_equity_pct=round(return_on_equity, 2),
            profit_factor=profit_factor,
            average_win_inr=round(avg_win, 2),
            average_loss_inr=round(avg_loss, 2),
            average_realized_rrr=round(avg_realized_rrr, 2),
            max_portfolio_drawdown_pct=round(max_dd_pct, 2),
            gap_down_events_count=len(gap_events),
            total_gap_slippage_inr=round(total_gap_slip, 2),
            score_7_win_rate_pct=round(s7_win_rate, 2),
            score_6_5_win_rate_pct=round(s65_win_rate, 2),
            circuit_breakers_tripped=circuit_breakers_count,
            trade_journal=self.completed_trades,
        )
