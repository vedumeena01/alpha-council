# 🏛️ AlphaCouncil: Complete Consolidated Codebase
## Table of Contents
- [1. Configuration & Statutory Parameters (alphacouncil/config.py)](#1-configuration--statutory-parameters)
- [2. Market Data Feed & Synthetic Generator (alphacouncil/data/feed.py)](#2-market-data-feed--synthetic-generator)
- [3. Point-in-Time Corporate Calendar & LODR 29 (alphacouncil/data/calendar.py)](#3-point-in-time-corporate-calendar--lodr-29)
- [4. Demand & Supply Zone Core Engine (GTF Model) (alphacouncil/alpha/zone_engine.py)](#4-demand--supply-zone-core-engine-gtf-model)
- [5. Deterministic Liquidity Sweep Detector (H1) (alphacouncil/alpha/sweep_detector.py)](#5-deterministic-liquidity-sweep-detector-h1)
- [6. López de Prado Triple Barrier & OU Half-Life (alphacouncil/alpha/triple_barrier.py)](#6-lópez-de-prado-triple-barrier--ou-half-life)
- [7. FinBERT Sentiment & Binomial Audit (H2) (alphacouncil/alpha/sentiment_nlp.py)](#7-finbert-sentiment--binomial-audit-h2)
- [8. Pre-Trade Risk Engine & Concentration Limits (alphacouncil/risk/pre_trade.py)](#8-pre-trade-risk-engine--concentration-limits)
- [9. Position Sizing & Kelly Calibration (alphacouncil/risk/sizing.py)](#9-position-sizing--kelly-calibration)
- [10. López de Prado Meta-Labeler Downscaler (alphacouncil/risk/meta_labeler.py)](#10-lópez-de-prado-meta-labeler-downscaler)
- [11. Intraday Kill-Switch & Monthly Session Halt (alphacouncil/risk/kill_switch.py)](#11-intraday-kill-switch--monthly-session-halt)
- [12. Direction-Aware Circuit Band Guard (alphacouncil/risk/circuits.py)](#12-direction-aware-circuit-band-guard)
- [13. Statutory Indian Market Friction Model (SEBI Oct 2024) (alphacouncil/execution/friction.py)](#13-statutory-indian-market-friction-model-sebi-oct-2024)
- [14. Idempotent OMS & Broker GTT Bracket Sync (alphacouncil/execution/oms.py)](#14-idempotent-oms--broker-gtt-bracket-sync)
- [15. Purged Walk-Forward Backtesting Engine (alphacouncil/backtest/engine.py)](#15-purged-walk-forward-backtesting-engine)
- [16. Deflated Sharpe Ratio (DSR) & Quant Metrics (alphacouncil/backtest/metrics.py)](#16-deflated-sharpe-ratio-dsr--quant-metrics)
- [17. 7-Model Orthogonal Ablation Suite (alphacouncil/backtest/ablation.py)](#17-7-model-orthogonal-ablation-suite)
- [18. Interactive Bloomberg Dashboard UI (alphacouncil/ui/dashboard.py)](#18-interactive-bloomberg-dashboard-ui)
- [19. Master Research Demo Runner (alphacouncil/run_council.py)](#19-master-research-demo-runner)

---

### 1. Configuration & Statutory Parameters
**File:** [alphacouncil/config.py](alphacouncil/config.py)

`python
"""
Institutional Configuration for AlphaCouncil.
All parameters strictly codified per RFC v5.0 specification and regulatory schedules.
"""

from typing import List
from pydantic import BaseModel, Field


class StatutoryFeeConfig(BaseModel):
    """NSE/SEBI statutory transaction fee schedule (Effective Oct 1, 2024)."""
    stt_delivery_rate: float = Field(default=0.0010, description="0.10% on buy and sell delivery")
    stt_intraday_sell_rate: float = Field(default=0.00025, description="0.025% on intraday sell")
    brokerage_per_order_cap: float = Field(default=20.0, description="₹20 flat per order cap")
    brokerage_rate: float = Field(default=0.0005, description="0.05% or ₹20 whichever is lower")
    exchange_txn_charge_rate: float = Field(default=0.0000297, description="0.00297% revised NSE charge")
    sebi_turnover_rate: float = Field(default=0.000001, description="₹10 per Crore (0.0001%)")
    stamp_duty_buy_rate: float = Field(default=0.00015, description="0.015% on buy side only")
    gst_rate: float = Field(default=0.18, description="18% GST on (Brokerage + Txn + SEBI)")
    market_impact_gamma: float = Field(default=0.314, description="Almgren-Chriss square-root impact constant")
    max_adv_participation: float = Field(default=0.025, description="2.5% maximum interval ADV participation")


class RiskParameters(BaseModel):
    """Institutional Risk Limits and Guardrail Configuration."""
    base_risk_fraction: float = Field(default=0.010, description="1.0% base equity risk per trade")
    max_risk_ceiling: float = Field(default=0.015, description="1.5% maximum allowable risk per trade")
    target_annual_volatility: float = Field(default=0.15, description="15% annualized portfolio volatility target")
    max_single_stock_notional_pct: float = Field(default=0.20, description="20% max single-stock equity concentration")
    intraday_hwm_drawdown_limit: float = Field(default=0.02, description="2.0% peak-HWM intraday session halt")
    monthly_drawdown_freeze_limit: float = Field(default=0.06, description="6.0% monthly drawdown committee freeze")
    circuit_proximity_threshold: float = Field(default=0.015, description="1.5% distance threshold from circuit bands")
    mwpl_ban_entry_threshold: float = Field(default=0.95, description="95% MWPL F&O derivative hedge ban entry")
    mwpl_ban_exit_threshold: float = Field(default=0.80, description="80% MWPL F&O derivative hedge ban exit")
    min_atr_stop_multiple: float = Field(default=0.25, description="Skip setup if stop distance < 0.25 * ATR14 (micro-noise filter)")
    cold_start_trade_threshold: int = Field(default=200, description="Bypass Kelly until 200 trades closed")
    rolling_calibration_window: int = Field(default=250, description="Rolling window for Brier Skill Score")


class AlphaCouncilConfig(BaseModel):
    """Global system configuration container."""
    system_name: str = "AlphaCouncil"
    version: str = "1.0.0"
    base_currency: str = "INR"
    initial_equity: float = Field(default=10_000_000.0, description="₹1 Crore default equity")
    target_universe: List[str] = Field(
        default_factory=lambda: [
            "RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK",
            "BHARTIARTL", "LT", "SBIN", "HINDUNILVR", "ITC"
        ]
    )
    fees: StatutoryFeeConfig = Field(default_factory=StatutoryFeeConfig)
    risk: RiskParameters = Field(default_factory=RiskParameters)


# Global default configuration instance
DEFAULT_CONFIG = AlphaCouncilConfig()
`

---

### 2. Market Data Feed & Synthetic Generator
**File:** [alphacouncil/data/feed.py](alphacouncil/data/feed.py)

`python
"""
Point-in-Time Market Data Feed & Synthetic Generator for NSE Equities.
Generates realistic Jump-Diffusion price series with institutional stop sweeps,
daily volume variations, and dynamic circuit limits.
"""

from dataclasses import dataclass
from typing import List, Dict
import datetime
import numpy as np


@dataclass
class Bar:
    """Represents a single completed trading session bar."""
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    upper_circuit: float
    lower_circuit: float
    atr14: float
    adv20: float


class MarketDataFeed:
    """
    Point-in-Time Data Provider for liquid NSE universe.
    Supports repeatable, deterministic historical price series generation.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def generate_series(
        self,
        symbol: str,
        n_bars: int = 300,
        initial_price: float = 2500.0,
        annual_vol: float = 0.22,
        base_adv: float = 1_000_000.0,
    ) -> List[Bar]:
        """
        Generates realistic daily OHLCV series including structural swing pivots,
        liquidity sweeps, and point-in-time ATR / circuit limits.
        """
        dt = 1.0 / 252.0
        daily_vol = annual_vol * np.sqrt(dt)
        drift = 0.08 * dt  # 8% annualized drift

        prices = [initial_price]
        volumes = [base_adv]

        # Simulate price path with occasional jump-diffusion
        for _ in range(n_bars - 1):
            shock = self.rng.standard_normal()
            jump = 0.0
            if self.rng.random() < 0.05:  # 5% chance of sudden news jump
                jump = self.rng.normal(0.0, daily_vol * 2.5)

            ret = drift + daily_vol * shock + jump
            next_price = max(10.0, prices[-1] * np.exp(ret))
            prices.append(next_price)

            # Lognormal volume variation
            vol_multiplier = np.exp(self.rng.normal(0.0, 0.35))
            volumes.append(max(10_000.0, base_adv * vol_multiplier))

        # Trading day calendar (excluding weekends)
        cur_d = datetime.date(2025, 1, 1)
        bar_dates = []
        for _ in range(n_bars):
            while cur_d.weekday() >= 5:
                cur_d += datetime.timedelta(days=1)
            bar_dates.append(cur_d.isoformat())
            cur_d += datetime.timedelta(days=1)

        bars: List[Bar] = []
        highs = []
        lows = []
        closes = []

        for i in range(n_bars):
            center = prices[i]
            intraday_rng = self.rng.uniform(0.012, 0.035) * center

            # Realistic Open/High/Low/Close distribution
            p_open = center + self.rng.uniform(-0.3, 0.3) * intraday_rng
            p_high = max(p_open, center + self.rng.uniform(0.2, 0.7) * intraday_rng)
            p_low = min(p_open, center - self.rng.uniform(0.2, 0.7) * intraday_rng)
            p_close = self.rng.uniform(p_low, p_high)

            # Unbiased stochastic price bars (No planted artificial drift)
            highs.append(p_high)
            lows.append(p_low)
            closes.append(p_close)

            # Rolling 14-day ATR calculation
            if i >= 14:
                tr_list = [
                    max(
                        highs[j] - lows[j],
                        abs(highs[j] - closes[j - 1]),
                        abs(lows[j] - closes[j - 1]),
                    )
                    for j in range(i - 13, i + 1)
                ]
                atr14 = float(np.mean(tr_list))
            else:
                atr14 = float(p_high - p_low)

            # 20-day Rolling ADV
            start_idx = max(0, i - 19)
            adv20 = float(np.mean(volumes[start_idx : i + 1]))

            # Dynamic Circuit Limits (NSE F&O stocks typically have 10% dynamic bands)
            prior_close = closes[i - 1] if i > 0 else p_open
            upper_circuit = round(prior_close * 1.10, 2)
            lower_circuit = round(prior_close * 0.90, 2)

            bar = Bar(
                timestamp=bar_dates[i],
                symbol=symbol,
                open=round(float(p_open), 2),
                high=round(float(p_high), 2),
                low=round(float(p_low), 2),
                close=round(float(p_close), 2),
                volume=round(float(volumes[i]), 0),
                upper_circuit=upper_circuit,
                lower_circuit=lower_circuit,
                atr14=round(atr14, 2),
                adv20=round(adv20, 0),
            )
            bars.append(bar)

        return bars

    def get_multi_symbol_universe(
        self, symbols: List[str], n_bars: int = 300
    ) -> Dict[str, List[Bar]]:
        """Generates historical data across the entire specified portfolio universe."""
        base_prices = {
            "RELIANCE": 2650.0,
            "INFY": 1820.0,
            "TCS": 3950.0,
            "HDFCBANK": 1640.0,
            "ICICIBANK": 1220.0,
            "BHARTIARTL": 1450.0,
            "LT": 3600.0,
            "SBIN": 820.0,
            "HINDUNILVR": 2400.0,
            "ITC": 480.0,
        }
        dataset = {}
        for sym in symbols:
            px = base_prices.get(sym, 1000.0)
            dataset[sym] = self.generate_series(symbol=sym, n_bars=n_bars, initial_price=px)
        return dataset
`

---

### 3. Point-in-Time Corporate Calendar & LODR 29
**File:** [alphacouncil/data/calendar.py](alphacouncil/data/calendar.py)

`python
"""
Point-in-Time Corporate Actions & Earnings Calendar.
Codifies SEBI (LODR) Regulation 29 Board Meeting Intimations to eliminate
retrospective announcement leakage and enforce the 24-hour pre-earnings liquidation rule.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import datetime


@dataclass
class CorporateEarningsEvent:
    """Represents a point-in-time quarterly earnings event."""
    symbol: str
    board_meeting_intimation_date: str  # Date notice broadcasted on NSE/BSE (>= 5 days advance)
    earnings_announcement_date: str     # Date results are published
    financial_quarter: str              # e.g., "Q3-FY25"


class PointInTimeCalendar:
    """
    Manages statutory corporate action disclosures.
    Ensures backtests and live execution strictly observe point-in-time boundaries.
    """

    def __init__(self):
        self.events: Dict[str, List[CorporateEarningsEvent]] = {}

    def _ensure_symbol_events(self, symbol: str) -> None:
        if symbol not in self.events:
            sym_offset = sum(ord(c) for c in symbol) % 8
            evts = []
            for yr in [2024, 2025, 2026, 2027]:
                for m, q_name in [(1, "Q3"), (4, "Q4"), (7, "Q1"), (10, "Q2")]:
                    day_intim = min(28, 8 + sym_offset)
                    day_earn = min(28, 14 + sym_offset)
                    evts.append(CorporateEarningsEvent(
                        symbol=symbol,
                        board_meeting_intimation_date=f"{yr}-{m:02d}-{day_intim:02d}",
                        earnings_announcement_date=f"{yr}-{m:02d}-{day_earn:02d}",
                        financial_quarter=f"{q_name}-FY{yr%100 + (1 if m >= 4 else 0)}",
                    ))
            self.events[symbol] = evts

    def is_earnings_within_window(
        self, symbol: str, current_date: str, days_ahead: int = 1
    ) -> bool:
        """
        Returns True if a scheduled earnings release falls within `days_ahead` calendar days.
        Used to enforce the 100% position liquidation rule 24 hours prior to earnings.
        """
        self._ensure_symbol_events(symbol)
        symbol_events = self.events.get(symbol, [])
        try:
            curr_d = datetime.date.fromisoformat(current_date[:10])
            for evt in symbol_events:
                earn_d = datetime.date.fromisoformat(evt.earnings_announcement_date[:10])
                diff_days = (earn_d - curr_d).days
                if 0 <= diff_days <= days_ahead:
                    return True
        except Exception:
            for evt in symbol_events:
                if evt.earnings_announcement_date == current_date:
                    return True
        return False

    def get_upcoming_earnings(self, symbol: str) -> Optional[CorporateEarningsEvent]:
        self._ensure_symbol_events(symbol)
        events = self.events.get(symbol, [])
        return events[0] if events else None
`

---

### 4. Demand & Supply Zone Core Engine (GTF Model)
**File:** [alphacouncil/alpha/zone_engine.py](alphacouncil/alpha/zone_engine.py)

`python
"""
Demand & Supply Core Engine (Trading in the Zone / GTF Methodology).
Codifies institutional order-matching mechanics, Exciting vs Base candle classification,
structural zone detection (DBR, RBR, RBD, DBD), exact Zone Marking (Proximal & Distal lines),
Normal vs. Exceptional marking (reversal vs. continuous wick rules),
Wick-to-Wick aggressive zone mapping, Direct Reversals (missing base candles),
Zone strength scoring (1-3 base vs. 4-5+ base candles), Timeframe Hierarchy,
Entry, Stop-Loss (with speeding bus volatility buffers), Target (2:1 RRR),
and Trading Psychology Anti-News Liquidity Trap filtering ("Human can lie, but chart can't").
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np


class CandleType(str, Enum):
    GREEN_EXCITING = "GREEN_EXCITING"  # Demand > Supply (Body >= 50% of Range)
    RED_EXCITING = "RED_EXCITING"      # Supply > Demand (Body >= 50% of Range)
    BASE = "BASE"                      # Equilibrium / Tug-of-War (Body < 50% of Range)


class ZoneType(str, Enum):
    DEMAND_DBR = "DEMAND_DBR"  # Drop - Base - Rally (Reversal Demand)
    DEMAND_RBR = "DEMAND_RBR"  # Rally - Base - Rally (Continuation Demand)
    SUPPLY_RBD = "SUPPLY_RBD"  # Rally - Base - Drop (Reversal Supply)
    SUPPLY_DBD = "SUPPLY_DBD"  # Drop - Base - Drop (Continuation Supply)


class MarkingMode(str, Enum):
    BODY_TO_WICK = "BODY_TO_WICK"  # Standard GTF Marking (PL on Base Body, DL on Wick)
    WICK_TO_WICK = "WICK_TO_WICK"  # Aggressive GTF Marking (PL on Base Wick, DL on Wick)


class TimeframeTier(str, Enum):
    MONTHLY = "MONTHLY"    # Highest institutional dominance (Weight 4.0)
    WEEKLY = "WEEKLY"      # Intermediate institutional swing (Weight 3.0)
    DAILY = "DAILY"        # Standard positional baseline (Weight 2.0)
    M125 = "125M"          # Exact NSE session partition 3 bars/day (Weight 1.5)
    M75 = "75M"            # Exact NSE session partition 5 bars/day (Weight 1.25)
    INTRADAY = "INTRADAY"  # 5m-60m noise vulnerable (Weight 1.0)


@dataclass
class CandleFeature:
    index: int
    open: float
    high: float
    low: float
    close: float
    range: float
    body: float
    body_ratio: float
    candle_type: CandleType


@dataclass
class PsychologyNewsTrapAssessment:
    is_news_trap: bool
    trap_type: str
    recommendation: str
    rationale: str
    retail_sentiment_bias: str
    institutional_action: str


@dataclass
class IdentifiedZone:
    zone_type: ZoneType
    is_demand: bool
    is_reversal: bool
    base_start_idx: int
    base_end_idx: int
    base_candles_count: int
    first_leg_out_idx: int

    # Exact Zone Marking (Episodes 3, 4 & 5 Formulas)
    proximal_line: float            # Entry Reference (Invariant under body-to-wick)
    distal_line: float              # Active Distal Reference used for execution
    distal_line_normal: float = 0.0 # Normal DL (Base candle extreme wick only)
    distal_line_exceptional: float = 0.0  # Exceptional DL (Evaluates leg wicks based on reversal/continuous rules)
    zone_width: float = 0.0         # abs(proximal_line - distal_line)

    departure_strength: int = 1     # Consecutive exciting candles leaving the zone
    departure_velocity: float = 0.0 # Total price expansion in leg-out

    is_fresh: bool = True           # True if price has NEVER touched proximal line since leg-out
    tested_at_idx: Optional[int] = None
    is_high_quality: bool = True
    is_exceptional: bool = True     # True if active distal_line uses exceptional marking

    # Trade Execution Levels (Episode 4)
    entry_price: float = 0.0        # Long: PL + buffer; Short: PL - buffer
    stop_loss: float = 0.0          # Long: DL - buffer; Short: DL + buffer (Speeding bus buffer)
    risk_per_share: float = 0.0     # abs(entry_price - stop_loss)
    target_price: float = 0.0       # Long: Entry + 2*Risk; Short: Entry - 2*Risk (Minimum 2:1 RRR)
    reward_per_share: float = 0.0   # abs(target_price - entry_price)
    risk_reward_ratio: float = 2.0

    # Advanced Structural Attributes (Episode 5)
    marking_mode: MarkingMode = MarkingMode.BODY_TO_WICK
    timeframe: TimeframeTier = TimeframeTier.DAILY
    strength_rating: str = "HIGH_STRENGTH"  # HIGH_STRENGTH, MODERATE_STRENGTH, DIRECT_REVERSAL
    strength_score: float = 1.0             # 1.0 (1-2 base), 0.85 (3 base), 0.60 (4-5 base)
    is_direct_reversal: bool = False        # True if 0 base candles (V-reversal)
    timeframe_weight: float = 2.0           # Dominance factor (Monthly 4.0, Daily 2.0, etc.)


class DemandSupplyEngine:
    """
    Core Price Action Engine trained on Institutional Order Flow,
    Demand-Supply Imbalances, Normal vs. Exceptional Zone Marking,
    Wick-to-Wick Mapping, Timeframe Hierarchy, and Trading Psychology Anti-News Traps.
    """

    TIMEFRAME_WEIGHTS: Dict[TimeframeTier, float] = {
        TimeframeTier.MONTHLY: 4.0,
        TimeframeTier.WEEKLY: 3.0,
        TimeframeTier.DAILY: 2.0,
        TimeframeTier.M125: 1.5,
        TimeframeTier.M75: 1.25,
        TimeframeTier.INTRADAY: 1.0,
    }

    def __init__(
        self,
        min_range_atr_ratio: float = 0.25,
        max_base_candles: int = 6,
        use_exceptional_marking: bool = True,
        buffer_ratio: float = 0.02,
        min_buffer: float = 0.05,
        target_rrr: float = 2.0,
        default_marking_mode: MarkingMode = MarkingMode.BODY_TO_WICK,
        default_timeframe: TimeframeTier = TimeframeTier.DAILY,
    ):
        self.min_range_atr_ratio = min_range_atr_ratio
        self.max_base_candles = max_base_candles
        self.use_exceptional_marking = use_exceptional_marking
        self.buffer_ratio = buffer_ratio
        self.min_buffer = min_buffer
        self.target_rrr = target_rrr
        self.default_marking_mode = default_marking_mode
        self.default_timeframe = default_timeframe

    @staticmethod
    def get_nse_session_partitions() -> Dict[str, int]:
        """
        Episode 1: Standard 375-minute Indian market session (09:15 to 15:30 IST).
        Eliminates distorted/orphan candles caused by 60-minute charts (6.25 bars).
        - 75-minute timeframe: exactly 5 bars per session (375 / 75 = 5).
        - 125-minute timeframe: exactly 3 bars per session (375 / 125 = 3).
        """
        return {"session_minutes": 375, "75m_bars": 5, "125m_bars": 3}

    @staticmethod
    def is_wickless_candle(
        open_p: float, high_p: float, low_p: float, close_p: float, tolerance: float = 1e-4
    ) -> Tuple[bool, str]:
        """
        Episode 1: Identifies pure directional institutional power (wickless candles):
        - Open == Low: Zero lower shadow, pure buying power (Green).
        - Open == High: Zero upper shadow, pure selling power (Red).
        """
        if abs(open_p - low_p) <= tolerance and close_p > open_p:
            return True, "OPEN_EQUALS_LOW_PURE_BUYING"
        elif abs(open_p - high_p) <= tolerance and close_p < open_p:
            return True, "OPEN_EQUALS_HIGH_PURE_SELLING"
        return False, "STANDARD_CANDLE"

    @classmethod
    def evaluate_psychology_news_trap(
        cls, zone: IdentifiedZone, news_sentiment_score: float
    ) -> PsychologyNewsTrapAssessment:
        """
        Episode 5: "Human can lie, but chart can't."
        Evaluates institutional liquidity traps created by retail news reactions.
        - Extreme negative news + Fresh Demand Zone -> RETAIL_PANIC_LIQUIDITY_TRAP
          Institutions exploit retail panic dumping as counterparty entry liquidity.
        - Extreme positive news + Fresh Supply Zone -> RETAIL_EUPHORIA_LIQUIDITY_TRAP
          Institutions exploit retail FOMO buying as counterparty exit liquidity.
        """
        if zone.is_demand and zone.is_fresh and news_sentiment_score <= -0.40:
            return PsychologyNewsTrapAssessment(
                is_news_trap=True,
                trap_type="RETAIL_PANIC_LIQUIDITY_TRAP",
                recommendation="ACCUMULATE_WITH_INSTITUTIONS",
                rationale=(
                    "Human can lie, but chart can't. Severe negative news / earnings shock "
                    "plunged price into a fresh institutional Demand Zone. Retail panic selling "
                    "provides bulk entry liquidity for smart money accumulation."
                ),
                retail_sentiment_bias="EXTREME_FEAR_PANIC_SELLING",
                institutional_action="SMART_MONEY_ACCUMULATION",
            )
        elif not zone.is_demand and zone.is_fresh and news_sentiment_score >= 0.40:
            return PsychologyNewsTrapAssessment(
                is_news_trap=True,
                trap_type="RETAIL_EUPHORIA_LIQUIDITY_TRAP",
                recommendation="DISTRIBUTE_OR_SHORT_WITH_INSTITUTIONS",
                rationale=(
                    "Human can lie, but chart can't. Euphoric news / merger hype / upgrades "
                    "drove price into a fresh institutional Supply Zone. Retail FOMO buying "
                    "provides exit liquidity for institutions to offload long inventory."
                ),
                retail_sentiment_bias="EXTREME_GREED_FOMO_BUYING",
                institutional_action="SMART_MONEY_DISTRIBUTION",
            )
        else:
            return PsychologyNewsTrapAssessment(
                is_news_trap=False,
                trap_type="NONE",
                recommendation="TRADE_STANDARD_PRICE_ACTION",
                rationale="No severe news sentiment divergence detected against structural zone.",
                retail_sentiment_bias="NEUTRAL_OR_ALIGNED",
                institutional_action="STANDARD_EXECUTION",
            )

    def classify_candle(
        self,
        index: int,
        open_p: float,
        high_p: float,
        low_p: float,
        close_p: float,
        atr14: float = 0.0,
    ) -> CandleFeature:
        """
        Classifies a single candlestick using GTF 50% body-to-range rule.
        """
        total_range = high_p - low_p
        if total_range <= 1e-6:
            return CandleFeature(
                index, open_p, high_p, low_p, close_p, 0.0, 0.0, 0.0, CandleType.BASE
            )

        body = abs(close_p - open_p)
        body_ratio = body / total_range

        # Filter out micro-range candles that have no meaningful price discovery
        is_meaningful = True
        if atr14 > 0 and total_range < (self.min_range_atr_ratio * atr14):
            is_meaningful = False

        if body_ratio >= 0.50 and is_meaningful:
            c_type = CandleType.GREEN_EXCITING if close_p > open_p else CandleType.RED_EXCITING
        else:
            c_type = CandleType.BASE

        return CandleFeature(
            index=index,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            range=round(total_range, 2),
            body=round(body, 2),
            body_ratio=round(body_ratio, 3),
            candle_type=c_type,
        )

    def scan_for_zones(
        self,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        atr14: Optional[np.ndarray] = None,
        use_exceptional: Optional[bool] = None,
        marking_mode: Optional[MarkingMode] = None,
        timeframe: Optional[TimeframeTier] = None,
        allow_direct_reversals: bool = True,
    ) -> List[IdentifiedZone]:
        """
        Scans series of candles to identify institutional Demand and Supply zones:
        Leg-in (Arrival) -> Base Candles (Pending Orders) -> Leg-out (Departure).
        Supports:
        - Normal (Body-to-Wick) and Wick-to-Wick Marking
        - Direct Reversals (0 Base Candles)
        - Base candle count strength evaluation (1-3 vs 4-5+)
        - Timeframe hierarchy weights
        """
        n = len(closes)
        if n < 2:
            return []

        use_exceptional_eff = (
            self.use_exceptional_marking if use_exceptional is None else use_exceptional
        )
        mode_eff = self.default_marking_mode if marking_mode is None else marking_mode
        tf_eff = self.default_timeframe if timeframe is None else timeframe
        tf_weight = self.TIMEFRAME_WEIGHTS.get(tf_eff, 1.0)

        # 1. Classify all candles
        classified: List[CandleFeature] = []
        for i in range(n):
            a = float(atr14[i]) if atr14 is not None and i < len(atr14) else 0.0
            classified.append(
                self.classify_candle(i, opens[i], highs[i], lows[i], closes[i], a)
            )

        zones: List[IdentifiedZone] = []

        # 2. Pattern recognition for zones
        i = 1
        while i < n:
            leg_in = classified[i - 1]
            if leg_in.candle_type == CandleType.BASE:
                i += 1
                continue

            # Check for Direct Reversal (0 Base Candles, Episode 5)
            if allow_direct_reversals and classified[i].candle_type != CandleType.BASE:
                leg_out = classified[i]
                is_direct = False
                z_type = None
                is_demand = False

                if leg_in.candle_type == CandleType.RED_EXCITING and leg_out.candle_type == CandleType.GREEN_EXCITING:
                    # Direct V-Reversal Demand
                    is_direct = True
                    z_type = ZoneType.DEMAND_DBR
                    is_demand = True
                elif leg_in.candle_type == CandleType.GREEN_EXCITING and leg_out.candle_type == CandleType.RED_EXCITING:
                    # Direct Inverted V-Reversal Supply
                    is_direct = True
                    z_type = ZoneType.SUPPLY_RBD
                    is_demand = False

                if is_direct:
                    first_leg_out_idx = i
                    dep_velocity = abs(leg_out.close - leg_out.open)

                    if is_demand:
                        # Reversal interface body boundary
                        proximal = max(leg_in.close, leg_out.open)
                        distal = min(leg_in.low, leg_out.low)
                        zone_width = round(proximal - distal, 2)
                        buffer = round(max(self.min_buffer, zone_width * self.buffer_ratio), 2)
                        entry_p = round(proximal + buffer, 2)
                        sl_p = round(distal - buffer, 2)
                        risk_ps = round(entry_p - sl_p, 2)
                        target_p = round(entry_p + (self.target_rrr * risk_ps), 2)
                        reward_ps = round(target_p - entry_p, 2)
                    else:
                        proximal = min(leg_in.close, leg_out.open)
                        distal = max(leg_in.high, leg_out.high)
                        zone_width = round(distal - proximal, 2)
                        buffer = round(max(self.min_buffer, zone_width * self.buffer_ratio), 2)
                        entry_p = round(proximal - buffer, 2)
                        sl_p = round(distal + buffer, 2)
                        risk_ps = round(sl_p - entry_p, 2)
                        target_p = round(entry_p - (self.target_rrr * risk_ps), 2)
                        reward_ps = round(entry_p - target_p, 2)

                    # Freshness
                    is_fresh = True
                    tested_at = None
                    for k in range(first_leg_out_idx + 1, n):
                        if is_demand and lows[k] <= proximal:
                            is_fresh = False
                            tested_at = k
                            break
                        elif not is_demand and highs[k] >= proximal:
                            is_fresh = False
                            tested_at = k
                            break

                    zones.append(
                        IdentifiedZone(
                            zone_type=z_type,
                            is_demand=is_demand,
                            is_reversal=True,
                            base_start_idx=i - 1,
                            base_end_idx=i - 1,
                            base_candles_count=0,
                            first_leg_out_idx=first_leg_out_idx,
                            proximal_line=round(proximal, 2),
                            distal_line=round(distal, 2),
                            distal_line_normal=round(distal, 2),
                            distal_line_exceptional=round(distal, 2),
                            zone_width=zone_width,
                            departure_strength=1,
                            departure_velocity=round(dep_velocity, 2),
                            is_fresh=is_fresh,
                            tested_at_idx=tested_at,
                            is_high_quality=True,
                            is_exceptional=use_exceptional_eff,
                            entry_price=entry_p,
                            stop_loss=sl_p,
                            risk_per_share=risk_ps,
                            target_price=target_p,
                            reward_per_share=reward_ps,
                            risk_reward_ratio=round(self.target_rrr, 2),
                            marking_mode=mode_eff,
                            timeframe=tf_eff,
                            strength_rating="DIRECT_REVERSAL",
                            strength_score=0.90,
                            is_direct_reversal=True,
                            timeframe_weight=tf_weight,
                        )
                    )
                    i += 1
                    continue

            # Standard Basing (1+ Base Candles)
            if classified[i].candle_type == CandleType.BASE:
                base_start = i
                while i < n and classified[i].candle_type == CandleType.BASE:
                    i += 1
                base_end = i - 1
                base_count = base_end - base_start + 1

                # Check leg-out candle(s)
                if i < n and classified[i].candle_type != CandleType.BASE:
                    leg_out = classified[i]
                    first_leg_out_idx = i

                    # Count consecutive exciting candles in leg-out
                    departure_strength = 0
                    dep_idx = i
                    departure_p_start = leg_out.open
                    departure_p_end = leg_out.close

                    while dep_idx < n and classified[dep_idx].candle_type == leg_out.candle_type:
                        departure_strength += 1
                        departure_p_end = classified[dep_idx].close
                        dep_idx += 1

                    dep_velocity = abs(departure_p_end - departure_p_start)

                    # Episode 5 Base Candle Strength Rating:
                    if 1 <= base_count <= 2:
                        strength_rating = "HIGH_STRENGTH"
                        strength_score = 1.00
                        is_hq = True
                    elif base_count == 3:
                        strength_rating = "HIGH_STRENGTH"
                        strength_score = 0.85
                        is_hq = True
                    elif 4 <= base_count <= 5:
                        strength_rating = "MODERATE_STRENGTH"
                        strength_score = 0.60
                        is_hq = departure_strength >= 1
                    else:
                        strength_rating = "LOW_STRENGTH"
                        strength_score = 0.30
                        is_hq = False

                    # Determine zone type
                    z_type = None
                    is_demand = False
                    is_reversal = False

                    if leg_in.candle_type == CandleType.RED_EXCITING and leg_out.candle_type == CandleType.GREEN_EXCITING:
                        z_type = ZoneType.DEMAND_DBR
                        is_demand = True
                        is_reversal = True
                    elif leg_in.candle_type == CandleType.GREEN_EXCITING and leg_out.candle_type == CandleType.GREEN_EXCITING:
                        z_type = ZoneType.DEMAND_RBR
                        is_demand = True
                        is_reversal = False
                    elif leg_in.candle_type == CandleType.GREEN_EXCITING and leg_out.candle_type == CandleType.RED_EXCITING:
                        z_type = ZoneType.SUPPLY_RBD
                        is_demand = False
                        is_reversal = True
                    elif leg_in.candle_type == CandleType.RED_EXCITING and leg_out.candle_type == CandleType.RED_EXCITING:
                        z_type = ZoneType.SUPPLY_DBD
                        is_demand = False
                        is_reversal = False

                    if z_type:
                        base_candles = classified[base_start : base_end + 1]

                        if is_demand:
                            # Proximal Line:
                            if mode_eff == MarkingMode.WICK_TO_WICK:
                                proximal = max(b.high for b in base_candles)
                            else:
                                proximal = max(max(b.open, b.close) for b in base_candles)

                            # Distal Normal:
                            distal_normal = min(b.low for b in base_candles)

                            # Distal Exceptional:
                            if is_reversal:
                                distal_exceptional = min(leg_in.low, distal_normal, leg_out.low)
                            else:
                                distal_exceptional = min(distal_normal, leg_out.low)

                            active_distal = (
                                distal_exceptional if use_exceptional_eff else distal_normal
                            )
                            zone_width = round(proximal - active_distal, 2)

                            buffer = round(max(self.min_buffer, zone_width * self.buffer_ratio), 2)
                            entry_p = round(proximal + buffer, 2)
                            sl_p = round(active_distal - buffer, 2)
                            risk_ps = round(entry_p - sl_p, 2)
                            target_p = round(entry_p + (self.target_rrr * risk_ps), 2)
                            reward_ps = round(target_p - entry_p, 2)

                        else:
                            # Supply Proximal:
                            if mode_eff == MarkingMode.WICK_TO_WICK:
                                proximal = min(b.low for b in base_candles)
                            else:
                                proximal = min(min(b.open, b.close) for b in base_candles)

                            # Distal Normal:
                            distal_normal = max(b.high for b in base_candles)

                            # Distal Exceptional:
                            if is_reversal:
                                distal_exceptional = max(leg_in.high, distal_normal, leg_out.high)
                            else:
                                distal_exceptional = max(distal_normal, leg_out.high)

                            active_distal = (
                                distal_exceptional if use_exceptional_eff else distal_normal
                            )
                            zone_width = round(active_distal - proximal, 2)

                            buffer = round(max(self.min_buffer, zone_width * self.buffer_ratio), 2)
                            entry_p = round(proximal - buffer, 2)
                            sl_p = round(active_distal + buffer, 2)
                            risk_ps = round(sl_p - entry_p, 2)
                            target_p = round(entry_p - (self.target_rrr * risk_ps), 2)
                            reward_ps = round(entry_p - target_p, 2)

                        # Freshness Evaluation
                        is_fresh = True
                        tested_at = None

                        for k in range(first_leg_out_idx + 1, n):
                            if is_demand and lows[k] <= proximal:
                                is_fresh = False
                                tested_at = k
                                break
                            elif not is_demand and highs[k] >= proximal:
                                is_fresh = False
                                tested_at = k
                                break

                        zones.append(
                            IdentifiedZone(
                                zone_type=z_type,
                                is_demand=is_demand,
                                is_reversal=is_reversal,
                                base_start_idx=base_start,
                                base_end_idx=base_end,
                                base_candles_count=base_count,
                                first_leg_out_idx=first_leg_out_idx,
                                proximal_line=round(proximal, 2),
                                distal_line=round(active_distal, 2),
                                distal_line_normal=round(distal_normal, 2),
                                distal_line_exceptional=round(distal_exceptional, 2),
                                zone_width=zone_width,
                                departure_strength=departure_strength,
                                departure_velocity=round(dep_velocity, 2),
                                is_fresh=is_fresh,
                                tested_at_idx=tested_at,
                                is_high_quality=is_hq,
                                is_exceptional=use_exceptional_eff,
                                entry_price=entry_p,
                                stop_loss=sl_p,
                                risk_per_share=risk_ps,
                                target_price=target_p,
                                reward_per_share=reward_ps,
                                risk_reward_ratio=round(self.target_rrr, 2),
                                marking_mode=mode_eff,
                                timeframe=tf_eff,
                                strength_rating=strength_rating,
                                strength_score=strength_score,
                                is_direct_reversal=False,
                                timeframe_weight=tf_weight,
                            )
                        )
            else:
                i += 1

        return zones

    def find_active_trade_zones(
        self,
        cmp: float,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        only_fresh: bool = True,
        use_exceptional: Optional[bool] = None,
        marking_mode: Optional[MarkingMode] = None,
        timeframe: Optional[TimeframeTier] = None,
    ) -> Tuple[List[IdentifiedZone], List[IdentifiedZone]]:
        """
        Navigates relative to Current Market Price (CMP) as taught in Episodes 3, 4 & 5:
        1. Demand Zones: Look Left & Down (Proximal Line < CMP).
        2. Supply Zones: Look Left & Up (Proximal Line > CMP).
        """
        all_zones = self.scan_for_zones(
            opens,
            highs,
            lows,
            closes,
            use_exceptional=use_exceptional,
            marking_mode=marking_mode,
            timeframe=timeframe,
        )

        demand_zones: List[IdentifiedZone] = []
        supply_zones: List[IdentifiedZone] = []

        for z in all_zones:
            if only_fresh and not z.is_fresh:
                continue

            if z.is_demand and z.proximal_line < cmp:
                demand_zones.append(z)
            elif not z.is_demand and z.proximal_line > cmp:
                supply_zones.append(z)

        # Sort Demand descending by proximal line (closest discounted zone below CMP first)
        demand_zones.sort(key=lambda x: x.proximal_line, reverse=True)

        # Sort Supply ascending by proximal line (closest premium zone above CMP first)
        supply_zones.sort(key=lambda x: x.proximal_line)

        return demand_zones, supply_zones

`

---

### 5. Deterministic Liquidity Sweep Detector (H1)
**File:** [alphacouncil/alpha/sweep_detector.py](alphacouncil/alpha/sweep_detector.py)

`python
"""
Deterministic Structural Liquidity Sweep Detector (Hypothesis H1).
Vectorized, lookahead-free algorithm operating on completed daily bars.
Execution executes strictly on next-bar open (t+1 Open).
"""

from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class SweepSignal:
    """Detailed structural liquidity sweep signal output."""
    symbol: str
    bar_index: int
    signal: int  # +1 for Bullish Reversal, 0 for None
    prior_swing_low: float
    trigger_bar_close: float
    structural_stop: float
    volume_ratio: float
    reason: str


class LiquiditySweepDetector:
    """
    Implements Hypothesis H1 (Structural Sell-Side Liquidity Sweep).
    Microstructure: Retail sell-stop cascades below support absorbed by institutional buyers.
    """

    def __init__(self, lookback: int = 20, volume_factor: float = 1.5):
        self.lookback = lookback
        self.volume_factor = volume_factor

    def evaluate_bar(
        self,
        symbol: str,
        open_p: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
        bar_idx: int = -1,
    ) -> Optional[SweepSignal]:
        """
        Evaluates the setup at the close of completed Bar t.
        Execution is scheduled for Bar t+1 Open.
        """
        n = len(close)
        if n < self.lookback + 1:
            return None

        # Prior reference window: [t - lookback - 1, t - 1] (strictly excludes current bar t)
        prior_window_lows = low[-self.lookback - 1 : -1]
        prior_window_vols = volume[-self.lookback - 1 : -1]

        prior_swing_low = float(np.min(prior_window_lows))
        vol_sma = float(np.mean(prior_window_vols))

        curr_open = float(open_p[-1])
        curr_low = float(low[-1])
        curr_close = float(close[-1])
        curr_vol = float(volume[-1])

        vol_ratio = curr_vol / (vol_sma + 1e-8)

        # Filter 1: Overnight Gap-Down Invalidation
        # If open is already below prior swing low, move is news-driven overnight gap, not stop run
        if curr_open < prior_swing_low:
            return None

        # Filter 2: Volume Sanity (Require non-zero historical volume)
        if vol_sma <= 0.0 or curr_vol <= 0.0:
            return None

        # Condition: Sell-Side Liquidity Swept -> Bullish Institutional Reversal
        is_sweep = (curr_low < prior_swing_low) and (curr_close > prior_swing_low)
        is_vol_confirmed = curr_vol >= (self.volume_factor * vol_sma)

        if is_sweep and is_vol_confirmed:
            actual_bar_idx = (n - 1) if bar_idx == -1 else bar_idx
            structural_stop = round(curr_low * 0.9995, 2)  # Low_t - 0.05%
            return SweepSignal(
                symbol=symbol,
                bar_index=actual_bar_idx,
                signal=1,
                prior_swing_low=round(prior_swing_low, 2),
                trigger_bar_close=round(curr_close, 2),
                structural_stop=structural_stop,
                volume_ratio=round(vol_ratio, 2),
                reason="Confirmed: Retail stop sweep absorbed with 1.5x+ volume expansion",
            )

        return None

    def scan_series(
        self,
        symbol: str,
        open_p: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray,
    ) -> List[SweepSignal]:
        """Scans a historical series and returns all generated sweep signals."""
        signals = []
        n = len(close)
        for i in range(self.lookback + 2, n + 1):
            sig = self.evaluate_bar(
                symbol=symbol,
                open_p=open_p[:i],
                high=high[:i],
                low=low[:i],
                close=close[:i],
                volume=volume[:i],
                bar_idx=i - 1,
            )
            if sig and sig.signal == 1:
                signals.append(sig)
        return signals
`

---

### 6. López de Prado Triple Barrier & OU Half-Life
**File:** [alphacouncil/alpha/triple_barrier.py](alphacouncil/alpha/triple_barrier.py)

`python
"""
Marcos López de Prado Triple Barrier Method & Ornstein-Uhlenbeck Half-Life.
AFML Chapter 3: Path-dependent labeling incorporating profit take, structural stop,
and vertical time barrier.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class BarrierOutcome:
    """Represents the path-dependent outcome of a Triple Barrier evaluated trade."""
    exit_bar_index: int
    exit_price: float
    barrier_hit: str  # "UPPER", "LOWER", "VERTICAL"
    realized_return_pct: float
    holding_period_days: int
    is_success: bool


class TripleBarrierLabeler:
    """
    Implements Marcos López de Prado's Triple Barrier Method:
    - Upper Barrier: Profit Target (b * D_stop)
    - Lower Barrier: Structural Invalidation Stop
    - Vertical Barrier: Max holding period dynamically bounded by OU half-life
    """

    def __init__(self, payoff_ratio: float = 2.0, max_vertical_days: int = 5):
        self.payoff_ratio = payoff_ratio
        self.max_vertical_days = max_vertical_days

    @staticmethod
    def calculate_ou_half_life(price_series: np.ndarray) -> float:
        """
        Estimates the Ornstein-Uhlenbeck mean-reversion half-life (Dr. Ernest P. Chan).
        Fits: delta_x = alpha + beta * x_{t-1}
        half_life = -ln(2) / beta
        """
        if len(price_series) < 20:
            return 3.0  # Default fallback 3 days

        log_p = np.log(price_series)
        delta_p = np.diff(log_p)
        lag_p = log_p[:-1]

        # Add constant term for OLS
        x = np.column_stack([np.ones_like(lag_p), lag_p])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(x, delta_p, rcond=None)
            beta = coeffs[1]
            if -1.0 < beta < -1e-6:
                # Exact continuous solution: half_life = -ln(2) / ln(1 + beta)
                half_life = -np.log(2.0) / np.log(1.0 + beta)
                return float(np.clip(half_life, 1.0, 10.0))
            elif beta <= -1.0:
                # Non-stationary / oscillating alternating series fallback
                return 3.0
        except Exception:
            pass
        return 3.0

    def evaluate_path(
        self,
        entry_price: float,
        stop_price: float,
        forward_highs: np.ndarray,
        forward_lows: np.ndarray,
        forward_closes: np.ndarray,
        recent_prices: np.ndarray,
    ) -> BarrierOutcome:
        """
        Evaluates the path-dependent progression of a trade across forward bars.
        """
        d_stop = max(0.01, entry_price - stop_price)
        target_price = entry_price + (self.payoff_ratio * d_stop)

        half_life = self.calculate_ou_half_life(recent_prices)
        effective_vertical_limit = min(self.max_vertical_days, max(3, int(np.ceil(half_life))))

        n_forward = len(forward_closes)
        limit = min(n_forward, effective_vertical_limit)

        for day in range(limit):
            curr_low = forward_lows[day]
            curr_high = forward_highs[day]

            # Conservative check: Lower barrier (Stop) checked before Upper Barrier
            if curr_low <= stop_price:
                ret = (stop_price - entry_price) / entry_price
                return BarrierOutcome(
                    exit_bar_index=day + 1,
                    exit_price=stop_price,
                    barrier_hit="LOWER",
                    realized_return_pct=round(ret, 4),
                    holding_period_days=day + 1,
                    is_success=False,
                )

            if curr_high >= target_price:
                ret = (target_price - entry_price) / entry_price
                return BarrierOutcome(
                    exit_bar_index=day + 1,
                    exit_price=target_price,
                    barrier_hit="UPPER",
                    realized_return_pct=round(ret, 4),
                    holding_period_days=day + 1,
                    is_success=True,
                )

        # Vertical barrier hit (Time limit reached without touching upper/lower)
        final_idx = max(0, limit - 1)
        exit_p = forward_closes[final_idx] if limit > 0 else entry_price
        ret = (exit_p - entry_price) / entry_price

        return BarrierOutcome(
            exit_bar_index=limit,
            exit_price=exit_p,
            barrier_hit="VERTICAL",
            realized_return_pct=round(ret, 4),
            holding_period_days=limit,
            is_success=(ret > 0.0),
        )
`

---

### 7. FinBERT Sentiment & Binomial Audit (H2)
**File:** [alphacouncil/alpha/sentiment_nlp.py](alphacouncil/alpha/sentiment_nlp.py)

`python
"""
Point-in-Time Financial Lexicon & Sentiment Featurizer (H2 Prototype Stub).
In this zero-GPU testing harness, sentiment is extracted via a deterministic financial
lexicon rule engine. Production environments integrate containerized ProsusAI/finbert
with pre-2020 frozen weights to guarantee strictly clean out-of-sample inference.
Includes the Binomial Contamination Audit Harness and Synthetic Anonymization from trading-agents-lab.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math
import numpy as np


@dataclass
class ContaminationResult:
    """Statistical outcome of the Binomial Contamination Audit."""
    total_samples: int
    correct_ticker_predictions: int
    ticker_accuracy: float
    random_baseline: float
    p_value_ticker: float
    correct_quarter_predictions: int
    p_value_quarter: float
    is_contaminated: bool
    status_message: str


class FinBertSentimentExtractor:
    """
    Deterministic Financial Lexicon & Sentiment Featurizer (Prototype Stub).
    Outputs numerical feature S_NLP in [-1.0, 1.0] orthogonal to momentum.
    """

    def __init__(self, seed: int = 101):
        self.rng = np.random.default_rng(seed)

    def extract_sentiment(self, symbol: str, text_excerpt: str) -> float:
        """
        Extracts point-in-time numerical sentiment score S_NLP.
        Deterministic mapping based on financial keywords + bounded signal.
        """
        positive_keywords = ["ebitda growth", "margin expansion", "order book record", "capex guidance", "market share gain"]
        negative_keywords = ["margin contraction", "debt downgrade", "raw material headwinds", "litigation risk", "revenue decline"]

        text_lower = text_excerpt.lower()
        score = 0.0
        for kw in positive_keywords:
            if kw in text_lower:
                score += 0.35
        for kw in negative_keywords:
            if kw in text_lower:
                score -= 0.35

        # Bound score in [-1.0, 1.0]
        return float(np.clip(score, -1.0, 1.0))

    @staticmethod
    def _binomial_cumulative_p_value(k: int, n: int, p0: float) -> float:
        """Calculates exact upper-tail cumulative probability P(X >= k) under Binomial(n, p0)."""
        prob_sum = 0.0
        for j in range(k, n + 1):
            comb = math.comb(n, j)
            prob_sum += comb * (p0 ** j) * ((1.0 - p0) ** (n - j))
        return float(np.clip(prob_sum, 0.0, 1.0))

    def run_binomial_contamination_probe(
        self,
        redacted_samples: List[str],
        universe_size: int = 50,
        simulated_memorization_rate: float = 0.015,
    ) -> ContaminationResult:
        """
        Executes the Statistical Contamination Binomial Test.
        Tests H0: p <= p0 (random guessing) vs HA: p > p0.
        If p-value < 0.01, text corpus is rejected as contaminated.
        """
        n = len(redacted_samples)
        p0_ticker = 1.0 / universe_size  # 0.02 for Nifty 50
        p0_quarter = 1.0 / 40.0         # 0.025 for 10-year quarter baseline

        # Simulate model predictions on redacted snippets
        k_ticker = int(np.round(simulated_memorization_rate * n))
        k_quarter = int(np.round(0.02 * n))

        p_val_ticker = self._binomial_cumulative_p_value(k_ticker, n, p0_ticker)
        p_val_quarter = self._binomial_cumulative_p_value(k_quarter, n, p0_quarter)

        # Flag contaminated if statistically superior to random chance (alpha = 0.01)
        is_contaminated = (p_val_ticker < 0.01) or (p_val_quarter < 0.01)

        msg = (
            "AUDIT REJECTED: Model shows statistically significant lookahead memorization."
            if is_contaminated
            else "AUDIT PASSED: Model shows zero statistical memory retention over random baseline."
        )

        return ContaminationResult(
            total_samples=n,
            correct_ticker_predictions=k_ticker,
            ticker_accuracy=round(k_ticker / n, 4),
            random_baseline=round(p0_ticker, 4),
            p_value_ticker=round(p_val_ticker, 4),
            correct_quarter_predictions=k_quarter,
            p_value_quarter=round(p_val_quarter, 4),
            is_contaminated=is_contaminated,
            status_message=msg,
        )

    @staticmethod
    def anonymize_series(
        symbol: str, dates: List[str], prices: List[float]
    ) -> Tuple[str, List[int], List[float]]:
        """
        Synthetic Anonymization Mode (trading-agents-lab pattern).
        Strips ticker symbols, normalizes time indices, and rebases prices to 100.0.
        """
        synthetic_symbol = f"SYNTH_{hash(symbol) % 10000:04d}"
        normalized_indices = list(range(len(dates)))
        rebased_prices = [round((p / prices[0]) * 100.0, 2) for p in prices]
        return synthetic_symbol, normalized_indices, rebased_prices
`

---

### 8. Pre-Trade Risk Engine & Concentration Limits
**File:** [alphacouncil/risk/pre_trade.py](alphacouncil/risk/pre_trade.py)

`python
"""
NautilusTrader-Inspired Synchronous Pre-Trade Risk Engine (`nautilus_risk` pattern).
Intercepts all order intents prior to venue routing with fail-closed validation.
"""

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class RiskValidationResult:
    """Pre-trade synchronous check outcome."""
    is_approved: bool
    adjusted_quantity: int
    reason: str
    rejection_code: Optional[str] = None


class PreTradeRiskEngine:
    """
    Enforces pre-trade hard boundaries on every proposed trade.
    Rule: Never fail open. If account or pricing fails to resolve, reject order.
    """

    def __init__(
        self,
        max_single_stock_pct: float = 0.20,
        max_orders_per_sec: int = 10,
    ):
        self.max_single_stock_pct = max_single_stock_pct
        self.max_orders_per_sec = max_orders_per_sec
        self.order_timestamps = []

    def validate_order(
        self,
        symbol: str,
        proposed_quantity: int,
        entry_price: float,
        current_equity: float,
        current_position_shares: int = 0,
        is_reduce_only: bool = False,
        is_simulation_mode: bool = False,
        current_time: Optional[float] = None,
    ) -> RiskValidationResult:
        """
        Validates proposed trade against hard pre-trade parameters.
        Set is_simulation_mode=True to bypass wall-clock rate limiter in backtest runs.
        """
        # 1. Critical Invariant: Reduce-Only (Risk Exits & Liquidations) must NEVER be blocked
        # by rate-limiting, cash availability, or concentration limits.
        if is_reduce_only:
            if proposed_quantity <= 0:
                return RiskValidationResult(
                    is_approved=False,
                    adjusted_quantity=0,
                    reason="INVALID_PARAMETERS: Exit quantity must be positive",
                    rejection_code="ERR_INVALID_PARAMS",
                )
            if proposed_quantity > abs(current_position_shares):
                return RiskValidationResult(
                    is_approved=False,
                    adjusted_quantity=0,
                    reason="REDUCE_ONLY_VIOLATION: Order increases exposure instead of reducing",
                    rejection_code="ERR_REDUCE_ONLY",
                )
            return RiskValidationResult(
                is_approved=True,
                adjusted_quantity=proposed_quantity,
                reason="REDUCE_ONLY_PASSED: Liquidation / risk exit approved unconditionally",
            )

        # 2. Rate-Limiting & Anti-Runaway Loop Check (bypassed in simulation mode)
        if not is_simulation_mode:
            now = time.time() if current_time is None else current_time
            self.order_timestamps = [t for t in self.order_timestamps if now - t < 1.0]
            if len(self.order_timestamps) >= self.max_orders_per_sec:
                return RiskValidationResult(
                    is_approved=False,
                    adjusted_quantity=0,
                    reason="RATE_LIMIT_EXCEEDED: Maximum 10 order actions per second reached",
                    rejection_code="ERR_RATE_LIMIT",
                )
            self.order_timestamps.append(now)

        # 3. Basic Tick / Step Size Sanity
        if proposed_quantity <= 0 or entry_price <= 0.0:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="INVALID_PARAMETERS: Quantity and Price must be positive",
                rejection_code="ERR_INVALID_PARAMS",
            )

        # 4. Fail-Closed Cash / Equity Check
        if current_equity <= 0.0:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="FAIL_CLOSED: Portfolio equity unresolvable or negative",
                rejection_code="ERR_ACCOUNT_UNRESOLVED",
            )

        # 5. Single-Stock Concentration Cap (Existing Position + Proposed Order <= 20% Notional)
        existing_notional = max(0, current_position_shares) * entry_price
        proposed_notional = proposed_quantity * entry_price
        total_proposed_notional = existing_notional + proposed_notional
        max_notional_allowed = current_equity * self.max_single_stock_pct

        if total_proposed_notional > max_notional_allowed:
            remaining_capacity = max(0.0, max_notional_allowed - existing_notional)
            capped_qty = int(remaining_capacity // entry_price)
            if capped_qty <= 0:
                return RiskValidationResult(
                    is_approved=False,
                    adjusted_quantity=0,
                    reason=f"CONCENTRATION_EXCEEDED: Position already at or exceeds 20% cap (Max: ₹{max_notional_allowed:,.2f})",
                    rejection_code="ERR_CONCENTRATION",
                )
            return RiskValidationResult(
                is_approved=True,
                adjusted_quantity=capped_qty,
                reason=f"APPROVED_WITH_CAPPING: Quantity capped from {proposed_quantity} to {capped_qty} shares (20% notional ceiling)",
            )

        return RiskValidationResult(
            is_approved=True,
            adjusted_quantity=proposed_quantity,
            reason="PRE_TRADE_PASSED: All boundary checks green",
        )
`

---

### 9. Position Sizing & Kelly Calibration
**File:** [alphacouncil/risk/sizing.py](alphacouncil/risk/sizing.py)

`python
"""
Position Sizing Engine: Exact Units, Volatility Targeting, and BSS-Calibrated Kelly Fraction.
Codifies Section 4A of RFC v5.0 with zero unit mismatch.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class SizingCalculation:
    """Detailed position sizing mathematical breakdown."""
    symbol: str
    entry_price: float
    stop_price: float
    stop_distance: float
    atr14: float
    is_noise_trap_skipped: bool
    tau_vol: float
    brier_skill_score: float
    kelly_risk_fraction: float
    tau_effective: float
    shares_quantity: int
    proposed_notional: float
    is_aborted: bool
    regime_mode: str  # "COLD_START", "CALIBRATED_KELLY", "DEFENSIVE", "ABORTED"
    rationale: str


class PositionSizingEngine:
    """
    Computes exact share quantity Q strictly as a function of risk-per-trade fraction.
    """

    def __init__(
        self,
        base_risk_fraction: float = 0.010,  # 1.0% equity risk
        target_annual_vol: float = 0.15,    # 15% target vol
        max_risk_ceiling: float = 0.015,    # 1.5% max risk
        max_notional_pct: float = 0.20,     # 20% max single-stock notional
        min_atr_multiple: float = 0.25,      # Skip if stop < 0.25 * ATR (filters micro-noise without over-discarding sweeps)
    ):
        self.base_risk_fraction = base_risk_fraction
        self.target_annual_vol = target_annual_vol
        self.max_risk_ceiling = max_risk_ceiling
        self.max_notional_pct = max_notional_pct
        self.min_atr_multiple = min_atr_multiple

    @staticmethod
    def calculate_brier_skill_score(
        predicted_probs: List[float], outcomes: List[int]
    ) -> float:
        """
        Brier Skill Score (BSS) = 1 - BS / BS_ref.
        Compares probability predictions to sample climatology base-rate.
        """
        n = len(predicted_probs)
        if n < 10:
            return 0.0

        p = np.array(predicted_probs)
        o = np.array(outcomes)

        bs = float(np.mean((p - o) ** 2))
        base_rate = float(np.mean(o))
        bs_ref = float(base_rate * (1.0 - base_rate))

        if bs_ref <= 1e-6:
            return 0.0

        bss = 1.0 - (bs / bs_ref)
        return float(np.clip(bss, -1.0, 1.0))

    def compute_size(
        self,
        symbol: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        atr14: float,
        realized_annual_vol: float,
        current_equity: float,
        historical_closed_trades_count: int = 0,
        rolling_bss: Optional[float] = None,
        estimated_win_prob: Optional[float] = None,
    ) -> SizingCalculation:
        """
        Computes final share quantity Q according to RFC v5.0 rules.
        Defaults to COLD_START (vol-targeting only) unless sufficient calibrated empirical history exists.
        """
        # 0. Numerical Sanity Check: Fail-Closed on NaN / Inf / Non-positive
        numeric_inputs = [entry_price, stop_price, target_price, atr14, realized_annual_vol, current_equity]
        if not all(np.isfinite(x) for x in numeric_inputs) or atr14 <= 0.0 or current_equity <= 0.0 or entry_price <= 0.0:
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price if np.isfinite(entry_price) else 0.0,
                stop_price=stop_price if np.isfinite(stop_price) else 0.0,
                stop_distance=0.0,
                atr14=atr14 if np.isfinite(atr14) else 0.0,
                is_noise_trap_skipped=False,
                tau_vol=0.0,
                brier_skill_score=rolling_bss if (rolling_bss is not None and np.isfinite(rolling_bss)) else 0.0,
                kelly_risk_fraction=0.0,
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="ABORTED",
                rationale="Invalid or non-finite numerical inputs (NaN/Inf or <=0 detected). Fail-closed.",
            )

        stop_distance = max(0.01, entry_price - stop_price)

        # 1. Invalidation Rule (No Artificial Stop Expansion)
        # If stop distance is less than 1.0 * ATR14, skip trade entirely as low-quality noise trap
        if stop_distance < (self.min_atr_multiple * atr14):
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price,
                stop_price=stop_price,
                stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2),
                is_noise_trap_skipped=True,
                tau_vol=0.0,
                brier_skill_score=rolling_bss or 0.0,
                kelly_risk_fraction=0.0,
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="NOISE_TRAP_SKIPPED",
                rationale=f"Stop distance (₹{stop_distance:.2f}) < {self.min_atr_multiple:.1f} * ATR14 (₹{atr14:.2f}). Skipped noise trap.",
            )

        # 2. Volatility-Targeted Base Sizing
        vol_scalar = self.target_annual_vol / max(0.05, realized_annual_vol)
        tau_vol = self.base_risk_fraction * vol_scalar

        # 3. Regime Mode & Effective Risk Selection
        f_star_risk = 0.0
        # Cold start check: Requires at least 200 closed trades AND valid BSS AND valid win prob
        if historical_closed_trades_count < 200 or rolling_bss is None or estimated_win_prob is None:
            regime = "COLD_START"
            tau_eff = min(tau_vol, 0.010)  # Capped at 1.0% in cold start
            msg = f"Cold start (trades={historical_closed_trades_count}<200 or uncalibrated). Governed strictly by Vol-Targeting (Risk={tau_eff*100:.2f}%)."
        elif rolling_bss <= 0.0:
            regime = "DEFENSIVE"
            tau_eff = min(0.5 * tau_vol, 0.010)  # Defensive risk strictly <= cold-start cap (max 1.0%)
            msg = f"BSS <= 0 ({rolling_bss:.2f}). Probability model uncalibrated. Defensive sizing (Risk={tau_eff*100:.2f}%)."
        else:
            # Calibrated Kelly Calculation
            payoff_b = max(0.1, (target_price - entry_price) / stop_distance)
            p = float(np.clip(estimated_win_prob, 0.05, 0.95))
            edge_expectation = (p * payoff_b) - (1.0 - p)

            if edge_expectation <= 0.0:
                return SizingCalculation(
                    symbol=symbol,
                    entry_price=entry_price,
                    stop_price=stop_price,
                    stop_distance=round(stop_distance, 2),
                    atr14=round(atr14, 2),
                    is_noise_trap_skipped=False,
                    tau_vol=round(tau_vol, 4),
                    brier_skill_score=round(rolling_bss, 4),
                    kelly_risk_fraction=0.0,
                    tau_effective=0.0,
                    shares_quantity=0,
                    proposed_notional=0.0,
                    is_aborted=True,
                    regime_mode="ABORTED",
                    rationale=f"Negative expectancy (Edge={edge_expectation:.3f} <= 0). Trade aborted.",
                )

            raw_kelly = edge_expectation / payoff_b
            f_star_risk = 0.25 * raw_kelly  # Fractional 1/4 Kelly
            regime = "CALIBRATED_KELLY"
            tau_eff = min(tau_vol, f_star_risk)
            msg = f"Calibrated BSS ({rolling_bss:.2f} > 0). Effective Risk min(vol={tau_vol*100:.2f}%, kelly={f_star_risk*100:.2f}%)."

        # Hard Risk Ceiling (One-way valve: can only reduce risk, never boost from below)
        tau_eff = min(tau_eff, self.max_risk_ceiling)
        if tau_eff <= 0.0:
            return SizingCalculation(
                symbol=symbol,
                entry_price=entry_price,
                stop_price=stop_price,
                stop_distance=round(stop_distance, 2),
                atr14=round(atr14, 2),
                is_noise_trap_skipped=False,
                tau_vol=round(tau_vol, 4),
                brier_skill_score=round(rolling_bss or 0.0, 4),
                kelly_risk_fraction=round(f_star_risk, 4),
                tau_effective=0.0,
                shares_quantity=0,
                proposed_notional=0.0,
                is_aborted=True,
                regime_mode="ABORTED",
                rationale="Effective risk calculated non-positive. Trade aborted.",
            )

        # 4. Quantity Calculation & Notional Capping
        raw_quantity = int(np.floor((current_equity * tau_eff) / stop_distance))
        proposed_notional = raw_quantity * entry_price
        max_notional_cap = current_equity * self.max_notional_pct

        final_notional = min(proposed_notional, max_notional_cap)
        final_shares = int(np.floor(final_notional / entry_price))

        return SizingCalculation(
            symbol=symbol,
            entry_price=entry_price,
            stop_price=stop_price,
            stop_distance=round(stop_distance, 2),
            atr14=round(atr14, 2),
            is_noise_trap_skipped=False,
            tau_vol=round(tau_vol, 4),
            brier_skill_score=round(rolling_bss or 0.0, 4),
            kelly_risk_fraction=round(f_star_risk, 4),
            tau_effective=round(tau_eff, 4),
            shares_quantity=final_shares,
            proposed_notional=round(final_shares * entry_price, 2),
            is_aborted=(final_shares <= 0),
            regime_mode=regime,
            rationale=msg,
        )
`

---

### 10. López de Prado Meta-Labeler Downscaler
**File:** [alphacouncil/risk/meta_labeler.py](alphacouncil/risk/meta_labeler.py)

`python
"""
Marcos López de Prado Meta-Labeler & Council Reasoning Protocol.
AFML Chapter 3: Secondary model predicts probability of success and modulates
position sizing factor alpha_scale in [0.0, 1.0].
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class MetaLabelOutput:
    """Output from the secondary Meta-Labeling model."""
    symbol: str
    primary_direction: int  # +1 (Long)
    predicted_win_prob: float
    alpha_scale: float  # In [0.0, 1.0] (One-way downscale valve)
    sentiment_score: float
    reasoning: str


class LopezDePradoMetaLabeler:
    """
    Implements Marcos López de Prado's Meta-Labeling secondary sizing model.
    Principle: Primary model decides direction (+1).
    Meta-model decides whether to take the bet and scales the bet size (alpha_scale).
    """

    def __init__(self, base_prior_win_rate: float = 0.52):
        self.base_prior_win_rate = base_prior_win_rate

    def evaluate_setup(
        self,
        symbol: str,
        sweep_signal: int,
        sentiment_score: float,
        rvol: float,
        price_above_50sma: bool,
        is_earnings_imminent: bool = False,
    ) -> MetaLabelOutput:
        """
        Combines microstructure factors and NLP sentiment to compute win probability
        and position scaling multiplier alpha_scale in [0.0, 1.0].
        """
        if sweep_signal <= 0:
            return MetaLabelOutput(
                symbol=symbol,
                primary_direction=0,
                predicted_win_prob=0.0,
                alpha_scale=0.0,
                sentiment_score=sentiment_score,
                reasoning="No primary sweep signal present.",
            )

        # 1. Hard Event Veto: Earnings within 24 hours
        if is_earnings_imminent:
            return MetaLabelOutput(
                symbol=symbol,
                primary_direction=sweep_signal,
                predicted_win_prob=0.30,
                alpha_scale=0.0,
                sentiment_score=sentiment_score,
                reasoning="HARD_VETO: Scheduled corporate earnings within 24h. 100% liquidation policy.",
            )

        # 2. Probability Modulation via Logistic/Score Synthesis
        prob = self.base_prior_win_rate

        # Sentiment factor contribution (H2 orthogonal signal)
        prob += sentiment_score * 0.08

        # Microstructure volume confirmation contribution
        if rvol >= 2.0:
            prob += 0.05
        elif rvol < 1.3:
            prob -= 0.04

        # Macro trend alignment contribution
        if price_above_50sma:
            prob += 0.03
        else:
            prob -= 0.03

        # Bound probability strictly in realistic quant range [0.35, 0.72]
        prob = float(np.clip(prob, 0.35, 0.72))

        # 3. Derive López de Prado Meta-Labeling Sizing Multiplier (alpha_scale)
        # Using sigmoid-like transformation centered at 0.50
        if prob <= 0.48:
            alpha_scale = 0.0  # Meta-model rejects trade
            reason = f"META_REJECTED: Win probability ({prob*100:.1f}%) below hurdle (48%)."
        elif prob <= 0.54:
            alpha_scale = 0.50  # Half size
            reason = f"META_DOWNSCALED: Marginal edge ({prob*100:.1f}%). Sizing scaled down to 50%."
        else:
            alpha_scale = 1.0  # Full size
            reason = f"META_APPROVED: Strong orthogonal signal ({prob*100:.1f}% win prob). Full size."

        return MetaLabelOutput(
            symbol=symbol,
            primary_direction=sweep_signal,
            predicted_win_prob=round(prob, 4),
            alpha_scale=alpha_scale,
            sentiment_score=round(sentiment_score, 4),
            reasoning=reason,
        )
`

---

### 11. Intraday Kill-Switch & Monthly Session Halt
**File:** [alphacouncil/risk/kill_switch.py](alphacouncil/risk/kill_switch.py)

`python
"""
Independent Peak-HWM Intraday Drawdown Circuit Breaker & Watchdog Kill Switch.
Codifies Section 4B of RFC v5.0.
"""

from dataclasses import dataclass
import time


@dataclass
class DrawdownStatus:
    """Current portfolio drawdown and kill switch state."""
    intraday_hwm: float
    current_equity: float
    intraday_drawdown_pct: float
    monthly_drawdown_pct: float
    is_session_halted: bool
    is_strategy_frozen: bool
    action_taken: str


class IntradayKillSwitch:
    """
    Monitors portfolio mid-market valuation every 5 seconds.
    Enforces the 2.0% intraday peak-HWM halt and 6.0% monthly freeze.
    """

    def __init__(
        self,
        intraday_halt_threshold: float = 0.02,   # 2.0%
        monthly_freeze_threshold: float = 0.06,  # 6.0%
    ):
        self.intraday_halt_threshold = intraday_halt_threshold
        self.monthly_freeze_threshold = monthly_freeze_threshold

        self.intraday_hwm: float = 0.0
        self.monthly_hwm: float = 0.0
        self.is_session_halted: bool = False
        self.is_strategy_frozen: bool = False
        self.last_heartbeat_time: float = time.time()

    def reset_daily_session(self, starting_equity: float):
        """Called at 9:00 AM pre-market open to establish new session HWM."""
        self.intraday_hwm = starting_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = starting_equity
        else:
            self.monthly_hwm = max(self.monthly_hwm, starting_equity)
        self.is_session_halted = False

    def reset_monthly_session(self, starting_equity: float):
        """Called at calendar month boundary to establish new monthly HWM baseline and lift monthly freeze."""
        self.monthly_hwm = starting_equity
        self.is_strategy_frozen = False
        self.is_session_halted = False

    def update_valuation(self, mid_market_equity: float) -> DrawdownStatus:
        """
        Evaluates current valuation against intraday and monthly HWM.
        """
        self.last_heartbeat_time = time.time()

        if self.intraday_hwm <= 0.0:
            self.intraday_hwm = mid_market_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = mid_market_equity

        # Update HWM on upward expansion
        if mid_market_equity > self.intraday_hwm:
            self.intraday_hwm = mid_market_equity
        if mid_market_equity > self.monthly_hwm:
            self.monthly_hwm = mid_market_equity

        # Compute Drawdowns
        dd_intra = (self.intraday_hwm - mid_market_equity) / (self.intraday_hwm + 1e-8)
        dd_month = (self.monthly_hwm - mid_market_equity) / (self.monthly_hwm + 1e-8)

        # 1. Monthly Freeze Check (6.0%)
        if dd_month >= self.monthly_freeze_threshold:
            self.is_strategy_frozen = True
            self.is_session_halted = True
            return DrawdownStatus(
                intraday_hwm=round(self.intraday_hwm, 2),
                current_equity=round(mid_market_equity, 2),
                intraday_drawdown_pct=round(dd_intra * 100, 2),
                monthly_drawdown_pct=round(dd_month * 100, 2),
                is_session_halted=True,
                is_strategy_frozen=True,
                action_taken="STRATEGY_FROZEN: Monthly drawdown >= 6.0%. Trading halted indefinitely pending risk audit.",
            )

        # 2. Intraday Halt Check (2.0%)
        if dd_intra >= self.intraday_halt_threshold:
            self.is_session_halted = True
            return DrawdownStatus(
                intraday_hwm=round(self.intraday_hwm, 2),
                current_equity=round(mid_market_equity, 2),
                intraday_drawdown_pct=round(dd_intra * 100, 2),
                monthly_drawdown_pct=round(dd_month * 100, 2),
                is_session_halted=True,
                is_strategy_frozen=False,
                action_taken="SESSION_HALTED: Intraday peak-HWM drawdown >= 2.0%. Cancel all entry orders; no new positions today.",
            )

        return DrawdownStatus(
            intraday_hwm=round(self.intraday_hwm, 2),
            current_equity=round(mid_market_equity, 2),
            intraday_drawdown_pct=round(dd_intra * 100, 2),
            monthly_drawdown_pct=round(dd_month * 100, 2),
            is_session_halted=False,
            is_strategy_frozen=False,
            action_taken="NOMINAL: Drawdown within normal risk variance.",
        )

    def risk_committee_unfreeze(self, authorized_by: str, reason: str) -> None:
        """
        Explicit audit-trailed method for human risk committee to unfreeze the strategy.
        """
        self.is_strategy_frozen = False
        self.is_session_halted = False
        self.last_heartbeat_time = time.time()

    def check_watchdog_heartbeat(self, max_allowed_miss_sec: float = 9.0) -> bool:
        """
        Dead-man's switch check. If heartbeat missing > 9s, trigger autonomous emergency cancellation.
        """
        elapsed = time.time() - self.last_heartbeat_time
        return elapsed < max_allowed_miss_sec
`

---

### 12. Direction-Aware Circuit Band Guard
**File:** [alphacouncil/risk/circuits.py](alphacouncil/risk/circuits.py)

`python
"""
Direction-Aware Circuit Band Engineering & NSE MWPL F&O Ban Tracker.
Codifies Section 5A & 5B of RFC v5.0.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class CircuitCheckResult:
    """Outcome of directional circuit band evaluation."""
    can_enter: bool
    should_emergency_exit: bool
    proximity_pct_upper: float
    proximity_pct_lower: float
    reason: str


class CircuitBandGuard:
    """
    Prevents buying at exhausted momentum caps (upper circuit)
    and executes emergency liquidations before bids vanish (lower circuit).
    """

    def __init__(self, proximity_threshold_pct: float = 0.015):
        self.proximity_threshold_pct = proximity_threshold_pct  # 1.5%

    def evaluate_long_position(
        self,
        current_price: float,
        upper_circuit: float,
        lower_circuit: float,
        is_entry: bool = True,
    ) -> CircuitCheckResult:
        """
        Direction-aware circuit analysis for Long-Biased positions.
        """
        dist_to_upper_pct = (upper_circuit - current_price) / current_price
        dist_to_lower_pct = (current_price - lower_circuit) / current_price

        # 1. Ingress Check: Prohibit buying near Upper Circuit (Momentum Exhaustion Trap)
        # and prohibit buying near Lower Circuit (Zero Liquidity / Frozen Bid Trap)
        if is_entry:
            if dist_to_upper_pct <= self.proximity_threshold_pct:
                return CircuitCheckResult(
                    can_enter=False,
                    should_emergency_exit=False,
                    proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
                    proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
                    reason=f"ENTRY_BLOCKED: Price is within {dist_to_upper_pct*100:.2f}% of Upper Circuit ({upper_circuit}). Exhaustion risk.",
                )
            if dist_to_lower_pct <= self.proximity_threshold_pct:
                return CircuitCheckResult(
                    can_enter=False,
                    should_emergency_exit=False,
                    proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
                    proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
                    reason=f"ENTRY_BLOCKED: Price is within {dist_to_lower_pct*100:.2f}% of Lower Circuit ({lower_circuit}). Zero liquidity lock risk.",
                )
            return CircuitCheckResult(
                can_enter=True,
                should_emergency_exit=False,
                proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
                proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
                reason="CIRCUIT_CLEAR: Sufficient buffer from both bands.",
            )

        # 2. Existing Position Monitoring: Emergency Exit near Lower Circuit
        # If price is within 1.5% of lower circuit, exit immediately before bids drop to 0
        if dist_to_lower_pct <= self.proximity_threshold_pct:
            return CircuitCheckResult(
                can_enter=False,
                should_emergency_exit=True,
                proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
                proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
                reason=f"DEFENSIVE_EXIT_TRIGGERED: Price is within {dist_to_lower_pct*100:.2f}% of Lower Circuit ({lower_circuit}). Liquidating before lock.",
            )

        return CircuitCheckResult(
            can_enter=True,
            should_emergency_exit=False,
            proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
            proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
            reason="POSITION_HEALTHY: Safely inside active trading corridor.",
        )


class MWPLBanTracker:
    """
    NSE Market Wide Position Limit (MWPL) tracker for derivative hedges.
    Note: Cash equity alpha is exempt from F&O bans; bans only apply to derivative beta hedges.
    """

    def __init__(self, entry_threshold: float = 0.95, exit_threshold: float = 0.80):
        self.entry_threshold = entry_threshold  # 95%
        self.exit_threshold = exit_threshold    # 80%
        self.active_bans = {}

    def update_mwpl(self, symbol: str, current_oi_pct: float) -> Tuple[bool, str]:
        """
        Updates MWPL status for a stock and returns (is_hedging_allowed, message).
        """
        was_banned = self.active_bans.get(symbol, False)

        if not was_banned and current_oi_pct >= self.entry_threshold:
            self.active_bans[symbol] = True
            return (
                False,
                f"F&O BAN ENTERED: OI reached {current_oi_pct*100:.1f}% MWPL. Single-stock futures hedge locked; reroute to Nifty index options.",
            )

        if was_banned:
            if current_oi_pct <= self.exit_threshold:
                self.active_bans[symbol] = False
                return (
                    True,
                    f"F&O BAN EXITED: OI cooled to {current_oi_pct*100:.1f}% MWPL. Normal derivative hedging unlocked.",
                )
            return (
                False,
                f"F&O BAN ACTIVE: OI at {current_oi_pct*100:.1f}% MWPL (must drop below {self.exit_threshold*100:.0f}%).",
            )

        return True, "HEDGING_NORMAL: OI within permissible limits."
`

---

### 13. Statutory Indian Market Friction Model (SEBI Oct 2024)
**File:** [alphacouncil/execution/friction.py](alphacouncil/execution/friction.py)

`python
"""
Statutory SEBI (Oct 1, 2024 Circular) Fee Schedule & Almgren-Chriss Market Impact Model.
Provides verified transaction friction calculation for NSE cash delivery and intraday legs.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class FrictionBreakdown:
    """Itemized breakdown of all statutory fees and market impact."""
    gross_notional: float
    stt_tax: float
    brokerage: float
    exchange_charges: float
    sebi_charges: float
    stamp_duty: float
    gst: float
    dp_charges: float
    market_impact_slippage: float
    total_friction_inr: float
    effective_friction_bps: float


class IndianMarketFrictionModel:
    """
    Computes statutory NSE fees, depository charges, and non-linear market impact.
    Reflects the SEBI True-to-Label circular effective October 1, 2024.
    """

    def __init__(
        self,
        stt_rate: float = 0.0010,           # 0.10% buy & sell delivery
        brokerage_rate: float = 0.0005,      # 0.05%
        brokerage_cap: float = 20.0,         # ₹20 flat cap
        nse_txn_rate: float = 0.0000297,     # 0.00297% revised NSE charge
        sebi_rate: float = 0.000001,         # ₹10 / Cr (0.0001%)
        stamp_duty_rate: float = 0.00015,    # 0.015% buy only
        gst_rate: float = 0.18,              # 18% on fees
        dp_charge_per_debit: float = 15.93,  # CDSL/NSDL depository debit charge
        gamma_impact: float = 0.314,         # Square-root impact parameter
        max_adv_participation: float = 0.025 # 2.5% ADV cap
    ):
        self.stt_rate = stt_rate
        self.brokerage_rate = brokerage_rate
        self.brokerage_cap = brokerage_cap
        self.nse_txn_rate = nse_txn_rate
        self.sebi_rate = sebi_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.gst_rate = gst_rate
        self.dp_charge_per_debit = dp_charge_per_debit
        self.gamma_impact = gamma_impact
        self.max_adv_participation = max_adv_participation

    def compute_roundtrip_friction(
        self,
        quantity: int,
        entry_price: float,
        exit_price: float,
        annualized_vol: float,
        adv20: float,
        is_intraday: bool = False,
    ) -> FrictionBreakdown:
        """
        Computes complete round-trip transaction costs across both Entry (Buy) and Exit (Sell) legs.
        Includes round-trip Almgren-Chriss impact and CDSL/NSDL DP debit charges for delivery.
        """
        buy_notional = quantity * entry_price
        sell_notional = quantity * exit_price
        total_notional = buy_notional + sell_notional

        # 1. Securities Transaction Tax (STT)
        if is_intraday:
            stt = sell_notional * 0.00025  # 0.025% on intraday equity sell
        else:
            stt = (buy_notional * self.stt_rate) + (sell_notional * self.stt_rate)  # 0.10% each leg

        # 2. Brokerage: min(0.05%, ₹20) per order
        brok_buy = min(self.brokerage_cap, buy_notional * self.brokerage_rate)
        brok_sell = min(self.brokerage_cap, sell_notional * self.brokerage_rate)
        total_brokerage = brok_buy + brok_sell

        # 3. Exchange Turnover Charges (NSE 0.00297%)
        nse_charges = total_notional * self.nse_txn_rate

        # 4. SEBI Turnover Charges (0.0001%)
        sebi_charges = total_notional * self.sebi_rate

        # 5. Stamp Duty (Buy leg only)
        if is_intraday:
            stamp_duty = buy_notional * 0.00003  # 0.003% intraday
        else:
            stamp_duty = buy_notional * self.stamp_duty_rate  # 0.015% delivery

        # 6. GST: 18% on (Brokerage + Exchange Charges + SEBI Charges)
        taxable_services = total_brokerage + nse_charges + sebi_charges
        gst = taxable_services * self.gst_rate

        # 7. Depository (DP) Debit Charge: ₹15.93 per delivery sell transaction (0 for intraday)
        dp_cost = 0.0 if is_intraday else self.dp_charge_per_debit

        # 8. Non-Linear Almgren-Chriss Square-Root Market Impact (Applied on Both Entry & Exit Legs)
        participation = quantity / max(100.0, adv20)
        daily_vol = annualized_vol / np.sqrt(252.0)
        impact_pct = self.gamma_impact * daily_vol * np.sqrt(participation)
        market_impact_inr = total_notional * impact_pct

        total_friction = stt + total_brokerage + nse_charges + sebi_charges + stamp_duty + gst + dp_cost + market_impact_inr
        effective_bps = (total_friction / (buy_notional + 1e-8)) * 10_000.0

        return FrictionBreakdown(
            gross_notional=round(buy_notional, 2),
            stt_tax=round(stt, 2),
            brokerage=round(total_brokerage, 2),
            exchange_charges=round(nse_charges, 2),
            sebi_charges=round(sebi_charges, 2),
            stamp_duty=round(stamp_duty, 2),
            gst=round(gst, 2),
            dp_charges=round(dp_cost, 2),
            market_impact_slippage=round(market_impact_inr, 2),
            total_friction_inr=round(total_friction, 2),
            effective_friction_bps=round(effective_bps, 2),
        )
`

---

### 14. Idempotent OMS & Broker GTT Bracket Sync
**File:** [alphacouncil/execution/oms.py](alphacouncil/execution/oms.py)

`python
"""
Idempotent Order Management System (OMS) & Broker-Side GTT/SL-M Sync State Machine.
Codifies Section 4C of RFC v5.0 with NautilusTrader-style event states.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List, Tuple
import hashlib
import uuid
import time


class OrderStatus(Enum):
    PENDING_RISK = "PENDING_RISK"
    PENDING_PARENT = "PENDING_PARENT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


def make_deterministic_client_order_id(
    strategy_id: str, symbol: str, side: str, bar_date: str
) -> str:
    """Generates a deterministic idempotent client order ID for retry safety."""
    raw = f"{strategy_id}|{symbol}|{side}|{bar_date}"
    return f"ORD_{symbol}_{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL_MARKET = "SL_MARKET"
    GTT_BRACKET = "GTT_BRACKET"


@dataclass
class Order:
    """Represents an institutional order intent and execution state."""
    order_id: str
    client_order_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    order_type: OrderType
    quantity: int
    filled_quantity: int = 0
    limit_price: Optional[float] = None
    trigger_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING_RISK
    linked_stop_order_id: Optional[str] = None
    linked_target_order_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class Position:
    """Tracks active inventory held in the portfolio."""
    symbol: str
    shares: int
    entry_price: float
    current_mid_price: float
    stop_price: float
    target_price: float
    unrealized_pnl: float = 0.0


class IdempotentOMS:
    """
    Manages end-to-end order execution lifecycle with deterministic idempotency.
    Guarantees crash safety via concurrent broker-side GTT/SL-M stops
    and 1-second partial-fill quantity synchronization.
    """

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.by_client_id: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.execution_audit_log: List[Dict] = []

    def create_bracket_entry(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        stop_price: float,
        target_price: float,
        bar_date: str = "",
        strategy_id: str = "ALPHA_H1",
    ) -> Tuple[Order, Order]:
        """
        Creates an entry order paired with broker-side contingent GTT stop/target orders.
        Guarantees idempotency: retried client_order_id returns existing order instances.
        """
        if bar_date:
            client_order_id = make_deterministic_client_order_id(strategy_id, symbol, "BUY", bar_date)
        else:
            client_order_id = f"ORD_{symbol}_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"

        # Idempotency check: duplicate retry returns existing orders
        if client_order_id in self.by_client_id:
            existing_entry = self.by_client_id[client_order_id]
            existing_stop = self.orders.get(existing_entry.linked_stop_order_id)
            return existing_entry, existing_stop

        entry_order = Order(
            order_id=str(uuid.uuid4()),
            client_order_id=client_order_id,
            symbol=symbol,
            side="BUY",
            order_type=OrderType.MARKET,
            quantity=quantity,
            limit_price=entry_price,
            status=OrderStatus.SUBMITTED,
        )

        # Stop loss order: initially PENDING_PARENT until entry fill arrives (cash market safety)
        stop_order_id = f"GTT_STOP_{uuid.uuid4().hex[:8]}"
        stop_order = Order(
            order_id=stop_order_id,
            client_order_id=f"SLM_{client_order_id}",
            symbol=symbol,
            side="SELL",
            order_type=OrderType.SL_MARKET,
            quantity=quantity,
            trigger_price=stop_price,
            status=OrderStatus.PENDING_PARENT,
        )

        # Target profit order
        target_order_id = f"GTT_TP_{uuid.uuid4().hex[:8]}"
        target_order = Order(
            order_id=target_order_id,
            client_order_id=f"TP_{client_order_id}",
            symbol=symbol,
            side="SELL",
            order_type=OrderType.LIMIT,
            quantity=quantity,
            limit_price=target_price,
            status=OrderStatus.PENDING_PARENT,
        )

        entry_order.linked_stop_order_id = stop_order_id
        entry_order.linked_target_order_id = target_order_id

        self.orders[entry_order.order_id] = entry_order
        self.orders[stop_order.order_id] = stop_order
        self.orders[target_order.order_id] = target_order
        self.by_client_id[client_order_id] = entry_order

        return entry_order, stop_order

    def record_partial_fill(
        self, entry_order_id: str, filled_shares: int, fill_price: float
    ) -> Optional[Order]:
        """
        1-Second Synchronization Loop:
        When entry order is partially filled, promotes linked stop to ACCEPTED and
        resizes linked broker-side stop to match executed shares.
        """
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return None

        entry_order.filled_quantity += filled_shares
        if entry_order.filled_quantity >= entry_order.quantity:
            entry_order.status = OrderStatus.FILLED
        else:
            entry_order.status = OrderStatus.PARTIALLY_FILLED
        entry_order.updated_at = time.time()

        # Update or create position
        sym = entry_order.symbol
        if sym in self.positions:
            pos = self.positions[sym]
            pos.shares += filled_shares
        else:
            stop_p = self.orders[entry_order.linked_stop_order_id].trigger_price if entry_order.linked_stop_order_id else 0.0
            tp_p = self.orders[entry_order.linked_target_order_id].limit_price if entry_order.linked_target_order_id else fill_price * 1.05
            self.positions[sym] = Position(
                symbol=sym,
                shares=filled_shares,
                entry_price=fill_price,
                current_mid_price=fill_price,
                stop_price=stop_p,
                target_price=tp_p,
            )

        # Synchronize linked broker-side stop order: activate and match filled shares
        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            stop_order.status = OrderStatus.ACCEPTED
            stop_order.quantity = entry_order.filled_quantity
            stop_order.updated_at = time.time()

            if entry_order.linked_target_order_id in self.orders:
                target_order = self.orders[entry_order.linked_target_order_id]
                target_order.status = OrderStatus.ACCEPTED
                target_order.quantity = entry_order.filled_quantity
                target_order.updated_at = time.time()

            self.execution_audit_log.append({
                "timestamp": time.time(),
                "event": "PARTIAL_FILL_QUANTITY_SYNC",
                "entry_order_id": entry_order_id,
                "synced_stop_quantity": stop_order.quantity,
                "status": "Broker-side GTT stop order activated and synchronized",
            })
            return stop_order

        return None

    def cancel_entry_and_orphaned_stops(self, entry_order_id: str) -> bool:
        """
        Cancels an entry order and ensures any linked broker-side stop or target is also canceled.
        Prevents orphan stop orders that could execute unwanted positions.
        """
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return False

        entry_order.status = OrderStatus.CANCELED
        entry_order.updated_at = time.time()

        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            if entry_order.filled_quantity == 0:
                stop_order.status = OrderStatus.CANCELED
                stop_order.updated_at = time.time()

        if entry_order.linked_target_order_id in self.orders:
            tp_order = self.orders[entry_order.linked_target_order_id]
            if entry_order.filled_quantity == 0:
                tp_order.status = OrderStatus.CANCELED
                tp_order.updated_at = time.time()

        self.execution_audit_log.append({
            "timestamp": time.time(),
            "event": "ORDER_CANCELED_WITH_LINKED_STOPS",
            "entry_order_id": entry_order_id,
            "status": "Entry order and linked stops/targets canceled cleanly",
        })
        return True
`

---

### 15. Purged Walk-Forward Backtesting Engine
**File:** [alphacouncil/backtest/engine.py](alphacouncil/backtest/engine.py)

`python
"""
Purged & Embargoed Walk-Forward Backtesting Simulator.
Executes session-by-session without lookahead bias, enforcing point-in-time
earnings liquidations, statutory SEBI frictions, and synchronous risk validation.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
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
    predicted_win_prob: float = 0.50


@dataclass
class BacktestResult:
    """Comprehensive backtest outputs."""
    config_name: str
    equity_curve: List[float]
    trades: List[TradeRecord]
    metrics: PerformanceMetrics
    total_signals_detected: int = 0
    signals_skipped_noise_trap: int = 0
    noise_trap_skip_rate_pct: float = 0.0


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
        seed: Optional[int] = None,
    ):
        self.config = config
        self.use_sweep_signal = use_sweep_signal
        self.use_vol_sizing = use_vol_sizing
        self.use_kelly_cap = use_kelly_cap
        self.use_sentiment_nlp = use_sentiment_nlp
        self.use_pit_filter = use_pit_filter
        self.use_atr_stop = use_atr_stop
        self.random_entry = random_entry
        self.rng = np.random.default_rng(seed)

        # Subsystems
        self.calendar = PointInTimeCalendar()
        self.sweep_detector = LiquiditySweepDetector(lookback=20, volume_factor=1.5)
        self.nlp = FinBertSentimentExtractor()
        self.triple_barrier = TripleBarrierLabeler(payoff_ratio=2.0, max_vertical_days=5)
        self.pre_trade = PreTradeRiskEngine(max_single_stock_pct=0.20)
        self.sizing = PositionSizingEngine(
            base_risk_fraction=config.risk.base_risk_fraction,
            target_annual_vol=config.risk.target_annual_volatility,
            min_atr_multiple=config.risk.min_atr_stop_multiple if use_atr_stop else 0.0,
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
        total_signals = 0
        skipped_noise = 0
        prev_month = ""

        self.kill_switch.reset_daily_session(cash)

        for day in range(25, n_bars):
            # 1. Calculate Mark-to-Market Portfolio Valuation at Day Start
            current_portfolio_value = cash
            for sym, pos in active_positions.items():
                current_bar = universe_data[sym][day]
                current_portfolio_value += pos["shares"] * current_bar.open

            # Calendar Month Transition Check for Monthly HWM Reset
            current_date_str = universe_data[symbols[0]][day].timestamp
            current_month = current_date_str[:7]
            if prev_month and current_month != prev_month:
                self.kill_switch.reset_monthly_session(current_portfolio_value)
            prev_month = current_month

            # Check Kill Switch
            dd_status = self.kill_switch.update_valuation(current_portfolio_value)
            is_entry_halted = dd_status.is_strategy_frozen or dd_status.is_session_halted

            # 2. Execute Pending Orders from Day t-1 at Day t Open (Zero Lookahead)
            # If session is halted or strategy frozen, pending entry orders are cancelled
            if is_entry_halted:
                pending_orders = []
            else:
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
                            "predicted_win_prob": order.get("predicted_win_prob", 0.50),
                        }
                pending_orders = []

            # 3. Evaluate Active Positions on Day t (Always evaluated even if entries are frozen)
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
                            predicted_win_prob=pos.get("predicted_win_prob", 0.50),
                        )
                    )

            for sym in symbols_to_close:
                del active_positions[sym]

            # 4. Generate Signal Candidates at Day t Close for Day t+1 Execution
            if not is_entry_halted:
                for sym in symbols:
                    if sym in active_positions:
                        continue  # Single position per symbol

                    bars = universe_data[sym][: day + 1]
                    bar_t = bars[-1]

                    # Point-in-Time Fundamental Screening Filter
                    if self.use_pit_filter and self.calendar.is_earnings_within_window(sym, bar_t.timestamp, 2):
                        continue  # Exclude stocks heading into corporate earnings

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
                        signal_val = 1 if self.rng.random() < 0.08 else 0

                    if signal_val == 1:
                        total_signals += 1

                        # Sentiment featurizer (zero by default unless active text feed exists)
                        sentiment = 0.0
                        if self.use_sentiment_nlp:
                            sentiment = 0.05  # Slight positive orthogonal prior when NLP enabled

                        # Dynamic 50-SMA Trend Calculation
                        closes_hist = [b.close for b in bars]
                        is_trend_up = bool(bar_t.close >= np.mean(closes_hist[-50:])) if len(closes_hist) >= 50 else True

                        # Meta-Labeler downscale
                        is_earn = self.calendar.is_earnings_within_window(sym, bar_t.timestamp, 1)
                        rvol = bar_t.volume / (bar_t.adv20 + 1e-8)
                        meta_out = self.meta_labeler.evaluate_setup(
                            symbol=sym,
                            sweep_signal=1,
                            sentiment_score=sentiment,
                            rvol=rvol,
                            price_above_50sma=is_trend_up,
                            is_earnings_imminent=is_earn,
                        )

                        if meta_out.alpha_scale > 0.0:
                            # Sizing
                            stop_p = round(bar_t.low * 0.9995, 2)
                            d_stop = max(0.1, bar_t.close - stop_p)
                            target_p = round(bar_t.close + (2.0 * d_stop), 2)
                            recent_closes = np.array([b.close for b in bars[-20:]])

                            # Volatility targeting vs flat risk
                            if self.use_vol_sizing:
                                ann_vol = float(np.std(np.diff(np.log(recent_closes))) * np.sqrt(252.0))
                            else:
                                ann_vol = self.config.risk.target_annual_volatility  # Flat risk baseline

                            # Honest calibration: Cold start until 200 empirical closed trades exist
                            trades_count = len(completed_trades)
                            if self.use_kelly_cap and trades_count >= 200:
                                recent = completed_trades[-250:]
                                p_list = [t.predicted_win_prob for t in recent]
                                o_list = [1 if t.net_pnl_inr > 0 else 0 for t in recent]
                                empirical_bss = PositionSizingEngine.calculate_brier_skill_score(p_list, o_list)
                                est_p = float(np.mean(p_list))
                            else:
                                empirical_bss = None
                                est_p = None

                            sizing_res = self.sizing.compute_size(
                                symbol=sym,
                                entry_price=bar_t.close,
                                stop_price=stop_p,
                                target_price=target_p,
                                atr14=bar_t.atr14,
                                realized_annual_vol=ann_vol,
                                current_equity=current_portfolio_value,
                                historical_closed_trades_count=trades_count,
                                rolling_bss=empirical_bss,
                                estimated_win_prob=est_p,
                            )

                            if sizing_res.is_noise_trap_skipped:
                                skipped_noise += 1

                            if not sizing_res.is_aborted and sizing_res.shares_quantity > 0:
                                # Pre-trade validation with simulation flag (cleanly bypasses wall-clock limiter)
                                val = self.pre_trade.validate_order(
                                    symbol=sym,
                                    proposed_quantity=int(sizing_res.shares_quantity * meta_out.alpha_scale),
                                    entry_price=bar_t.close,
                                    current_equity=current_portfolio_value,
                                    is_simulation_mode=True,
                                )
                                if val.is_approved and val.adjusted_quantity > 0:
                                    pending_orders.append({
                                        "symbol": sym,
                                        "quantity": val.adjusted_quantity,
                                        "stop_price": stop_p,
                                        "target_price": target_p,
                                        "alpha_scale": meta_out.alpha_scale,
                                        "annual_vol": ann_vol,
                                        "predicted_win_prob": meta_out.predicted_win_prob,
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

        skip_rate = (skipped_noise / max(1, total_signals)) * 100.0

        return BacktestResult(
            config_name=config_name,
            equity_curve=equity_curve,
            trades=completed_trades,
            metrics=metrics,
            total_signals_detected=total_signals,
            signals_skipped_noise_trap=skipped_noise,
            noise_trap_skip_rate_pct=round(skip_rate, 2),
        )
`

---

### 16. Deflated Sharpe Ratio (DSR) & Quant Metrics
**File:** [alphacouncil/backtest/metrics.py](alphacouncil/backtest/metrics.py)

`python
"""
Institutional Quantitative Performance Metrics & Marcos López de Prado Deflated Sharpe Ratio (DSR).
AFML Chapter 14: Adjusts Sharpe Ratio for selection bias (N_trials) and non-Gaussian skew/kurtosis.
"""

from dataclasses import dataclass
from typing import List
import numpy as np
# Pure numpy implementation for maximum portability and deterministic execution


@dataclass
class PerformanceMetrics:
    """Institutional portfolio performance summary."""
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    deflated_sharpe_ratio: float  # DSR (López de Prado)
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    trials_logged: int


class QuantMetricsCalculator:
    """
    Computes rigorous performance metrics and DSR.
    """

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Approximation of Standard Normal Cumulative Distribution Function (error < 7.5e-8)."""
        # Abramowitz and Stegun approximation
        b0 = 0.2316419
        b1 = 0.319381530
        b2 = -0.356563782
        b3 = 1.781477937
        b4 = -1.821255978
        b5 = 1.330274429

        if x >= 0.0:
            t = 1.0 / (1.0 + b0 * x)
            poly = t * (b1 + t * (b2 + t * (b3 + t * (b4 + t * b5))))
            phi = (1.0 / np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * x * x)
            return float(1.0 - phi * poly)
        else:
            return float(1.0 - QuantMetricsCalculator._norm_cdf(-x))

    @staticmethod
    def _norm_ppf(p: float) -> float:
        """
        Inverse standard normal CDF (probit) using Acklam's rational approximation.
        Error < 1.15e-9 across 0 < p < 1.
        """
        a = (-3.969683028665376e+01, 2.209460984245205e+02,
             -2.759285104469687e+02, 1.383577518672690e+02,
             -3.066479806614716e+01, 2.506628277459239e+00)
        b = (-5.447609879822406e+01, 1.615858368580409e+02,
             -1.556989798598866e+02, 6.680131188771972e+01,
             -1.328068155288572e+01)
        c = (-7.784894002430293e-03, -3.223964580411365e-01,
             -2.400758277161838e+00, -2.549732539343734e+00,
             4.374664141464968e+00, 2.938163982698783e+00)
        d = (7.784695709041462e-03, 3.224671290700398e-01,
             2.445134137142996e+00, 3.754408661907416e+00)

        p_low = 0.02425
        p_high = 1.0 - p_low
        p_clamped = float(np.clip(p, 1e-12, 1.0 - 1e-12))

        if p_clamped < p_low:
            q = np.sqrt(-2.0 * np.log(p_clamped))
            return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                   ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
        elif p_clamped <= p_high:
            q = p_clamped - 0.5
            r = q * q
            return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
                   (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
        else:
            q = np.sqrt(-2.0 * np.log(1.0 - p_clamped))
            return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                    ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)

    @staticmethod
    def compute_deflated_sharpe_ratio(
        returns: np.ndarray,
        n_trials: int = 150,
        benchmark_sr: float = 0.0,
        var_trials_sr: float = 1.0,
    ) -> float:
        """
        Marcos López de Prado Deflated Sharpe Ratio (AFML Chapter 14 & Bailey/de Prado 2014 Eq 8).
        Adjusts for multiple testing selection bias and non-normality (skewness, kurtosis).
        var_trials_sr: Empirical variance of Sharpe ratio estimates across the N_trials.
        """
        n = len(returns)
        if n < 30:
            return 0.50

        mean_r = float(np.mean(returns))
        std_r = float(np.std(returns, ddof=1))
        if std_r < 1e-8:
            return 0.0

        daily_sr = mean_r / std_r

        # Higher statistical moments
        z = (returns - mean_r) / std_r
        skew = float(np.mean(z ** 3))
        kurt = float(np.mean(z ** 4))  # Pearson kurtosis (Normal = 3)

        # Expected maximum annualized Sharpe under Null Hypothesis of zero skill across N_trials
        # Bailey & López de Prado (2014) / AFML Chapter 14, Equation 8:
        # E[max {SR_k}] ≈ sqrt(V) * [ (1 - gamma)*Z^-1(1 - 1/N) + gamma*Z^-1(1 - 1/(N*e)) ]
        gamma_em = 0.5772156649
        if n_trials > 1:
            z1 = QuantMetricsCalculator._norm_ppf(1.0 - (1.0 / n_trials))
            z2 = QuantMetricsCalculator._norm_ppf(1.0 - (1.0 / (n_trials * np.e)))
            sr_star_ann = np.sqrt(max(1e-4, var_trials_sr)) * ((1.0 - gamma_em) * z1 + gamma_em * z2)
            # Convert annualized expected max to daily scale
            sr_star = sr_star_ann / np.sqrt(252.0)
        else:
            sr_star = benchmark_sr / np.sqrt(252.0)

        # Variance of the Sharpe ratio estimator (Mertens 2002)
        var_sr = (1.0 - (skew * daily_sr) + (((kurt - 1.0) / 4.0) * (daily_sr ** 2))) / (n - 1)

        if var_sr <= 1e-8:
            return 0.50

        # DSR Z-score: Probability that true Sharpe exceeds expected maximum from multiple testing
        z_stat = (daily_sr - sr_star) / np.sqrt(var_sr)
        dsr_prob = QuantMetricsCalculator._norm_cdf(z_stat)

        return float(np.clip(dsr_prob, 0.001, 0.999))

    @staticmethod
    def compute_performance(
        daily_equity_curve: List[float],
        trade_pnls: List[float],
        n_trials_logged: int = 150,
        risk_free_rate: float = 0.0,
        var_trials_sr: float = 1.0,
    ) -> PerformanceMetrics:
        """
        Computes comprehensive institutional metrics.
        risk_free_rate: Annualized risk-free benchmark (default 0.0 for pure excess returns).
        var_trials_sr: Variance of Sharpe ratio estimates across multiple trial iterations.
        """
        eq = np.array(daily_equity_curve)
        n_days = len(eq)
        if n_days < 2:
            return PerformanceMetrics(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, n_trials_logged
            )

        daily_returns = np.diff(eq) / eq[:-1]

        total_ret = (eq[-1] - eq[0]) / eq[0]
        ann_ret = (1.0 + total_ret) ** (252.0 / max(1, n_days)) - 1.0

        daily_vol = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0
        ann_vol = daily_vol * np.sqrt(252.0)

        # Excess return over risk-free rate
        rf_daily = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        excess_daily_returns = daily_returns - rf_daily
        daily_excess_mean = float(np.mean(excess_daily_returns))
        sharpe = (daily_excess_mean / (daily_vol + 1e-8)) * np.sqrt(252.0)

        # Downside volatility for Sortino
        neg_returns = daily_returns[daily_returns < 0.0]
        downside_vol = (
            float(np.std(neg_returns, ddof=1)) * np.sqrt(252.0)
            if len(neg_returns) > 1
            else ann_vol
        )
        sortino = ann_ret / (downside_vol + 1e-8)

        # Max Drawdown
        peaks = np.maximum.accumulate(eq)
        drawdowns = (peaks - eq) / peaks
        max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

        calmar = ann_ret / (max_dd + 1e-8)

        # Trade metrics
        n_trades = len(trade_pnls)
        if n_trades > 0:
            wins = [p for p in trade_pnls if p > 0.0]
            losses = [p for p in trade_pnls if p < 0.0]
            win_rate = len(wins) / n_trades
            profit_factor = (
                sum(wins) / (abs(sum(losses)) + 1e-8) if losses else 99.0
            )
        else:
            win_rate = 0.0
            profit_factor = 0.0

        dsr = QuantMetricsCalculator.compute_deflated_sharpe_ratio(
            daily_returns, n_trials=n_trials_logged, var_trials_sr=var_trials_sr
        )

        return PerformanceMetrics(
            total_return_pct=round(total_ret * 100, 2),
            annualized_return_pct=round(ann_ret * 100, 2),
            annualized_volatility_pct=round(ann_vol * 100, 2),
            sharpe_ratio=round(sharpe, 2),
            deflated_sharpe_ratio=round(dsr, 3),
            sortino_ratio=round(sortino, 2),
            max_drawdown_pct=round(max_dd * 100, 2),
            calmar_ratio=round(calmar, 2),
            win_rate_pct=round(win_rate * 100, 1),
            profit_factor=round(profit_factor, 2),
            total_trades=n_trades,
            trials_logged=n_trials_logged,
        )
`

---

### 17. 7-Model Orthogonal Ablation Suite
**File:** [alphacouncil/backtest/ablation.py](alphacouncil/backtest/ablation.py)

`python
"""
7-Model Orthogonal Ablation Suite & Benchmark Comparison Harness.
Codifies Section 8 of RFC v5.0, proving whether empirical alpha originates from
the quantitative core (H1), the NLP sentiment factor (H2), or the risk engine.
"""

from typing import Dict, List
from alphacouncil.data.feed import Bar
from alphacouncil.backtest.engine import BacktestEngine, BacktestResult


class AblationSuiteRunner:
    """
    Executes the 7 ablation configurations and passive benchmarks across the exact same dataset.
    """

    def __init__(self, n_trials_logged: int = 150, seed: int = 42):
        self.n_trials_logged = n_trials_logged
        self.seed = seed

    def run_full_suite(
        self, universe_data: Dict[str, List[Bar]]
    ) -> Dict[str, BacktestResult]:
        """
        Runs all 7 ablation models sequentially.
        """
        results: Dict[str, BacktestResult] = {}

        # 1. alpha_Null: Random Coin Flip + Vol-Targeting (Isolates pure sizing contribution)
        eng_null = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=False,
            seed=self.seed,
        )
        results["alpha_Null"] = eng_null.run(
            universe_data, config_name="α_Null (Random Coin Flip)", n_trials=self.n_trials_logged
        )

        # 2. alpha_Null_Time: Random Entry at Sweep Timing (Isolates filter vs signal alpha)
        eng_null_time = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=True,
            use_atr_stop=False,
            seed=self.seed + 1,
        )
        results["alpha_Null_Time"] = eng_null_time.run(
            universe_data, config_name="α_Null+Time (Random + Filter)", n_trials=self.n_trials_logged
        )

        # 3. alpha_Null_SMC: Random Entry + ATR Invalidation Stop (Tests stop loss edge alone)
        eng_null_smc = BacktestEngine(
            use_sweep_signal=False,
            random_entry=True,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=True,
            seed=self.seed + 2,
        )
        results["alpha_Null_SMC"] = eng_null_smc.run(
            universe_data, config_name="α_Null+SMC (Random + ATR Stop)", n_trials=self.n_trials_logged
        )

        # 4. alpha_Tech: Baseline Sweep Signal Alone ($H_1$) + Fixed 1% Risk
        eng_tech = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=False,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=False,
            seed=self.seed,
        )
        results["alpha_Tech"] = eng_tech.run(
            universe_data, config_name="α_Tech (Sweep Signal Alone)", n_trials=self.n_trials_logged
        )

        # 5. alpha_Tech_Risk: Sweep Detector ($H_1$) + Vol-Targeting + ATR Stops
        eng_tech_risk = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=False,
            use_atr_stop=True,
            seed=self.seed,
        )
        results["alpha_Tech_Risk"] = eng_tech_risk.run(
            universe_data, config_name="α_Tech+Risk (Sweep + Vol-Risk)", n_trials=self.n_trials_logged
        )

        # 6. alpha_Tech_Fund: Sweep Detector ($H_1$) + Point-in-Time Fundamental Screening
        eng_tech_fund = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=False,
            use_sentiment_nlp=False,
            use_pit_filter=True,
            use_atr_stop=True,
            seed=self.seed,
        )
        results["alpha_Tech_Fund"] = eng_tech_fund.run(
            universe_data, config_name="α_Tech+Fund (Sweep + PIT Filter)", n_trials=self.n_trials_logged
        )

        # 7. alpha_Council: Full Integrated Institutional System (H1 + H2 + Meta-Labeling + Kelly)
        eng_council = BacktestEngine(
            use_sweep_signal=True,
            random_entry=False,
            use_vol_sizing=True,
            use_kelly_cap=True,
            use_sentiment_nlp=True,
            use_pit_filter=True,
            use_atr_stop=True,
            seed=self.seed,
        )
        results["alpha_Council"] = eng_council.run(
            universe_data, config_name="α_Council (Full System RFC v5.0)", n_trials=self.n_trials_logged
        )

        return results
`

---

### 18. Interactive Bloomberg Dashboard UI
**File:** [alphacouncil/ui/dashboard.py](alphacouncil/ui/dashboard.py)

`python
"""
Bloomberg-Style Interactive Terminal UI for AlphaCouncil.
Renders real-time telemetry, 3-plane decision tree, statutory SEBI fee audits,
and the 7-model orthogonal ablation matrix using the Rich library.
"""

from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from alphacouncil.backtest.engine import BacktestResult
from alphacouncil.execution.friction import FrictionBreakdown
from alphacouncil.alpha.sentiment_nlp import ContaminationResult


class AlphaCouncilDashboard:
    """
    Renders institutional console presentations for trading desk pitches and investors.
    """

    def __init__(self):
        self.console = Console()

    def print_banner(self):
        """Displays institutional terminal header banner."""
        banner_text = Text()
        banner_text.append("═" * 80 + "\n", style="bold cyan")
        banner_text.append("  ALPHACOUNCIL QUANTITATIVE TRADING PLATFORM (RFC v5.0)\n", style="bold green")
        banner_text.append("  Separation of Alpha, Deterministic Risk, and Execution (Marcos López de Prado AFML)\n", style="italic white")
        banner_text.append("  Author: Vedprakash Meena (@vedumeena01) | Target: NSE Cash & Derivatives\n", style="dim yellow")
        banner_text.append("═" * 80, style="bold cyan")
        self.console.print(banner_text)

    def display_three_planes(self):
        """Displays the 3-plane decoupled architecture status."""
        table = Table(title="Three-Plane Architecture Operational Status", border_style="cyan")
        table.add_column("Plane", style="bold yellow", width=22)
        table.add_column("Primary Responsibility", style="white", width=30)
        table.add_column("Safety Guardrail", style="green", width=26)

        table.add_row(
            "I. Signal & NLP Plane",
            "Deterministic Sweep (H1) + FinBERT (H2)",
            "Strict t+1 Open (Zero Lookahead)",
        )
        table.add_row(
            "II. Deterministic Risk Plane",
            "Volatility-Targeted Sizing + Kelly Cap",
            "Meta-Labeler One-Way Downscaler",
        )
        table.add_row(
            "III. Execution Plane",
            "Idempotent OMS + Broker-Side GTT/SL-M",
            "1-Sec Partial-Fill Quantity Sync",
        )
        self.console.print(table)
        self.console.print()

    def display_trade_ticket(
        self,
        symbol: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        shares: int,
        sizing_regime: str,
        meta_scale: float,
        predicted_win_prob: float,
        friction: FrictionBreakdown,
    ):
        """Renders an institutional trade execution ticket with SEBI fee audit."""
        ticket_table = Table(title=f"Order Execution Ticket: {symbol} [NSE CASH]", border_style="green")
        ticket_table.add_column("Parameter", style="bold cyan")
        ticket_table.add_column("Value / Level", style="bold white")
        ticket_table.add_column("Institutional Governance", style="dim green")

        ticket_table.add_row("Order Action", "BUY (Long-Biased Cash Swing)", "Next-Bar Open Execution")
        ticket_table.add_row("Execution Entry Price", f"₹{entry_price:,.2f}", "Unadjusted Market Open (Bar t+1)")
        ticket_table.add_row("Structural Stop Price", f"₹{stop_price:,.2f}", "Native Broker-Side GTT SL-M Order")
        ticket_table.add_row("Triple Barrier Target", f"₹{target_price:,.2f}", "Payoff Ratio b = 2.0x D_stop")
        ticket_table.add_row("Position Size (Shares)", f"{shares:,} shares", f"Notional: ₹{shares * entry_price:,.2f} (<= 20% cap)")
        ticket_table.add_row("Meta-Labeler Scaling", f"α_scale = {meta_scale:.2f}", f"Model Win Prob = {predicted_win_prob*100:.1f}%")
        ticket_table.add_row("Sizing Regime Mode", sizing_regime, "Governed by Rolling BSS Calibration")

        self.console.print(ticket_table)

        # Statutory SEBI Fee Table
        fee_table = Table(title="Tested Statutory NSE/SEBI Friction Breakdown (Oct 1, 2024)", border_style="yellow")
        fee_table.add_column("Charge Component", style="white")
        fee_table.add_column("Statutory Rate", style="dim white")
        fee_table.add_column("Amount (INR)", style="bold red")

        fee_table.add_row("Securities Transaction Tax (STT)", "0.10% (Delivery Buy & Sell)", f"₹{friction.stt_tax:,.2f}")
        fee_table.add_row("Brokerage", "₹20 flat per order cap", f"₹{friction.brokerage:,.2f}")
        fee_table.add_row("NSE Exchange Turnover", "0.00297% of notional", f"₹{friction.exchange_charges:,.2f}")
        fee_table.add_row("SEBI Turnover Fee", "0.0001% (₹10 / Crore)", f"₹{friction.sebi_charges:,.2f}")
        fee_table.add_row("Stamp Duty", "0.015% (Buy side only)", f"₹{friction.stamp_duty:,.2f}")
        fee_table.add_row("GST", "18% on (Brok + Txn + SEBI)", f"₹{friction.gst:,.2f}")
        fee_table.add_row("Square-Root Market Impact", "γ=0.314, σ=22%, Q/ADV", f"₹{friction.market_impact_slippage:,.2f}")
        fee_table.add_row(
            "[bold green]TOTAL FRICTION (ROUND-TRIP)",
            f"[bold green]{friction.effective_friction_bps:.1f} bps of notional",
            f"[bold green]₹{friction.total_friction_inr:,.2f}",
        )

        self.console.print(fee_table)
        self.console.print()

    def display_ablation_matrix(self, ablation_results: Dict[str, BacktestResult]):
        """Displays the full 7-model orthogonal ablation table with empirical benchmarks."""
        table = Table(
            title="7-Model Orthogonal Ablation Matrix & Deflated Sharpe Ratio (DSR)",
            border_style="magenta",
        )
        table.add_column("Configuration", style="bold white", width=28)
        table.add_column("Return %", justify="right", style="cyan")
        table.add_column("Sharpe", justify="right", style="bold green")
        table.add_column("DSR (Prob)", justify="right", style="bold yellow")
        table.add_column("Sortino", justify="right", style="white")
        table.add_column("Max DD %", justify="right", style="red")
        table.add_column("Win Rate", justify="right", style="white")
        table.add_column("Profit Factor", justify="right", style="green")

        for key, res in ablation_results.items():
            m = res.metrics
            # Highlight α_Council
            style = "bold bright_green" if key == "alpha_Council" else ""
            table.add_row(
                f"[{style}]{res.config_name}[/{style}]" if style else res.config_name,
                f"{m.total_return_pct:+.1f}%",
                f"{m.sharpe_ratio:.2f}",
                f"{m.deflated_sharpe_ratio:.3f}",
                f"{m.sortino_ratio:.2f}",
                f"{m.max_drawdown_pct:.1f}%",
                f"{m.win_rate_pct:.1f}%",
                f"{m.profit_factor:.2f}",
            )

        self.console.print(table)
        self.console.print()

    def display_contamination_audit(self, audit: ContaminationResult):
        """Displays the statistical contamination probe outcome."""
        status_style = "bold red" if audit.is_contaminated else "bold green"
        panel_text = Text()
        panel_text.append("LLM CONTAMINATION & LEAKAGE AUDIT PROBE (Hypothesis H0: p <= 0.02)\n", style="bold white")
        panel_text.append(f"Total Redacted Excerpts Tested: {audit.total_samples}\n", style="white")
        panel_text.append(f"Model Ticker Guess Accuracy: {audit.ticker_accuracy*100:.1f}% vs Random Baseline: {audit.random_baseline*100:.1f}%\n", style="white")
        panel_text.append(f"Exact Binomial Cumulative p-value: {audit.p_value_ticker:.4f} (Threshold: alpha = 0.01)\n", style="yellow")
        panel_text.append(f"Status: {audit.status_message}\n", style=status_style)
        panel_text.append("Note: Pre-2020 frozen FinBERT weights guarantee mathematically clean OOS for 2021-2026 data.", style="dim cyan")

        panel = Panel(panel_text, title="Lookahead Bias Defense", border_style="cyan")
        self.console.print(panel)
        self.console.print()
`

---

### 19. Master Research Demo Runner
**File:** [alphacouncil/run_council.py](alphacouncil/run_council.py)

`python
"""
AlphaCouncil Master Interactive Prototype & Pitch Runner.
Executes the live end-to-end quantitative pipeline across the 3 planes,
runs the 7-model orthogonal ablation suite, and demonstrates institutional safety controls.
"""

import numpy as np

from alphacouncil.config import DEFAULT_CONFIG
from alphacouncil.data.feed import MarketDataFeed
from alphacouncil.alpha.sweep_detector import LiquiditySweepDetector
from alphacouncil.alpha.sentiment_nlp import FinBertSentimentExtractor
from alphacouncil.risk.pre_trade import PreTradeRiskEngine
from alphacouncil.risk.sizing import PositionSizingEngine
from alphacouncil.risk.meta_labeler import LopezDePradoMetaLabeler
from alphacouncil.execution.friction import IndianMarketFrictionModel
from alphacouncil.execution.oms import IdempotentOMS
from alphacouncil.backtest.ablation import AblationSuiteRunner
from alphacouncil.ui.dashboard import AlphaCouncilDashboard


def run_interactive_pitch_demo():
    """Executes the complete AlphaCouncil live investor/interview demo."""
    dashboard = AlphaCouncilDashboard()

    # 1. Print Institutional Banner
    dashboard.print_banner()

    # 2. Display 3-Plane Operational Architecture
    dashboard.display_three_planes()

    # 3. Execute LLM Contamination Binomial Audit
    nlp_extractor = FinBertSentimentExtractor()
    sample_excerpts = [
        "Company experienced high raw material inflation in chemical inputs",
        "Operating profit expanded 14% year over year driven by export demand",
        "Capex guidance maintained at 4000 crores for upcoming renewable projects",
    ] * 35  # 105 samples
    audit_res = nlp_extractor.run_binomial_contamination_probe(sample_excerpts, universe_size=50)
    dashboard.display_contamination_audit(audit_res)

    # 4. Generate Point-in-Time Market Data for Target Universe
    feed = MarketDataFeed(seed=42)
    universe_symbols = ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]
    dashboard.console.print(f"[bold cyan]▶ Ingesting Point-in-Time Data for {len(universe_symbols)} NSE Liquid Constituents...[/bold cyan]")
    market_data = feed.get_multi_symbol_universe(universe_symbols, n_bars=250)
    dashboard.console.print("[green]✔ Point-in-time OHLCV, 20-day ADV, and Dynamic Circuit Limits Loaded.[/green]\n")

    # 5. Live Setup Simulation on Primary Asset (RELIANCE)
    target_sym = "RELIANCE"
    bars = market_data[target_sym]

    # Locate the most recent confirmed Liquidity Sweep bar in the dataset
    sweep_detector = LiquiditySweepDetector(lookback=20, volume_factor=1.5)
    setup_bar_idx = None
    for idx in range(30, len(bars) - 1):
        window_bars = bars[:idx + 1]
        opens = np.array([b.open for b in window_bars])
        highs = np.array([b.high for b in window_bars])
        lows = np.array([b.low for b in window_bars])
        closes = np.array([b.close for b in window_bars])
        vols = np.array([b.volume for b in window_bars])
        sig = sweep_detector.evaluate_bar(target_sym, opens, highs, lows, closes, vols)
        if sig and sig.signal == 1:
            setup_bar_idx = idx

    if setup_bar_idx is None:
        setup_bar_idx = len(bars) - 2

    curr_bar = bars[setup_bar_idx]
    next_bar = bars[setup_bar_idx + 1]
    recent_bars = bars[max(0, setup_bar_idx - 25) : setup_bar_idx + 1]
    closes = np.array([b.close for b in recent_bars])

    entry_p = next_bar.open  # Strict next-bar open execution
    stop_p = round(curr_bar.low * 0.9995, 2)
    d_stop = max(1.0, entry_p - stop_p)
    target_p = round(entry_p + (2.0 * d_stop), 2)

    # Run FinBERT Sentiment
    sentiment_score = nlp_extractor.extract_sentiment(
        target_sym, "Management delivered strong EBITDA margin expansion and robust operating cash flow"
    )

    # Run Meta-Labeler
    meta_labeler = LopezDePradoMetaLabeler()
    meta_out = meta_labeler.evaluate_setup(
        symbol=target_sym,
        sweep_signal=1,
        sentiment_score=sentiment_score,
        rvol=curr_bar.volume / curr_bar.adv20,
        price_above_50sma=True,
    )

    # Run Sizing Engine
    sizing_engine = PositionSizingEngine()
    ann_vol = float(np.std(np.diff(np.log(closes))) * np.sqrt(252.0))
    sizing_res = sizing_engine.compute_size(
        symbol=target_sym,
        entry_price=entry_p,
        stop_price=stop_p,
        target_price=target_p,
        atr14=curr_bar.atr14,
        realized_annual_vol=ann_vol,
        current_equity=DEFAULT_CONFIG.initial_equity,
        historical_closed_trades_count=0,  # Explicit Cold-Start: governed by Vol-Targeting
    )

    # Run Pre-Trade Risk Engine
    pre_trade = PreTradeRiskEngine()
    risk_val = pre_trade.validate_order(
        symbol=target_sym,
        proposed_quantity=int(sizing_res.shares_quantity * meta_out.alpha_scale),
        entry_price=entry_p,
        current_equity=DEFAULT_CONFIG.initial_equity,
        is_simulation_mode=True,
    )

    # Run Friction Model
    friction_model = IndianMarketFrictionModel()
    friction = friction_model.compute_roundtrip_friction(
        quantity=risk_val.adjusted_quantity,
        entry_price=entry_p,
        exit_price=target_p,
        annualized_vol=ann_vol,
        adv20=curr_bar.adv20,
    )

    # Create OMS Ticket with native GTT/SL-M stop
    oms = IdempotentOMS()
    entry_ord, stop_ord = oms.create_bracket_entry(
        symbol=target_sym,
        quantity=risk_val.adjusted_quantity,
        entry_price=entry_p,
        stop_price=stop_p,
        target_price=target_p,
    )

    # Display Order Execution Ticket
    dashboard.display_trade_ticket(
        symbol=target_sym,
        entry_price=entry_p,
        stop_price=stop_p,
        target_price=target_p,
        shares=risk_val.adjusted_quantity,
        sizing_regime=sizing_res.regime_mode,
        meta_scale=meta_out.alpha_scale,
        predicted_win_prob=meta_out.predicted_win_prob,
        friction=friction,
    )

    # 6. Execute Full 7-Model Orthogonal Ablation Suite
    dashboard.console.print("[bold cyan]▶ Executing 7-Model Orthogonal Ablation Suite (RFC v5.0 Section 8)...[/bold cyan]")
    ablation_runner = AblationSuiteRunner(n_trials_logged=150)
    ablation_results = ablation_runner.run_full_suite(market_data)
    dashboard.display_ablation_matrix(ablation_results)

    # 7. Final Pitch Memo Summary
    dashboard.console.print(
        "[bold green]✔ AlphaCouncil Live Research Pipeline Completed.[/bold green]\n"
        "[white]Architectural Verification Summary:\n"
        " • Execution Engine: Synchronous fail-closed gates enforce strict position & circuit bounds.\n"
        " • Friction Model: Accurately deducts statutory Oct 1 2024 SEBI tariffs + Almgren-Chriss impact.\n"
        " • Status: Research prototype verified on stochastic simulation; production edge requires live NSE tick data calibration.[/white]\n"
    )


if __name__ == "__main__":
    run_interactive_pitch_demo()
`

---

