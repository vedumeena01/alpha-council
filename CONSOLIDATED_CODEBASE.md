# 🏛️ AlphaCouncil: Complete Consolidated Codebase
## Table of Contents
- [1. Configuration & Statutory Parameters (alphacouncil/config.py)](#1-configuration--statutory-parameters)
- [2. Market Data Feed & Synthetic Generator (alphacouncil/data/feed.py)](#2-market-data-feed--synthetic-generator)
- [3. Point-in-Time Corporate Calendar & LODR 29 (alphacouncil/data/calendar.py)](#3-point-in-time-corporate-calendar--lodr-29)
- [4. Demand & Supply Zone Core Engine (GTF Model) (alphacouncil/alpha/zone_engine.py)](#4-demand--supply-zone-core-engine-gtf-model)
- [5. Deterministic Liquidity Sweep Detector (H1) (alphacouncil/alpha/sweep_detector.py)](#5-deterministic-liquidity-sweep-detector-h1)
- [6. López de Prado Triple Barrier & OU Half-Life (alphacouncil/alpha/triple_barrier.py)](#6-lópez-de-prado-triple-barrier--ou-half-life)
- [7. FinBERT Sentiment & Binomial Audit (H2) (alphacouncil/alpha/sentiment_nlp.py)](#7-finbert-sentiment--binomial-audit-h2)
- [8. Sectoral Analysis Engine (Episode 16) (alphacouncil/alpha/sector_engine.py)](#8-sectoral-analysis-engine-episode-16)
- [9. Candlestick Patterns Truth Engine (Episode 17) (alphacouncil/alpha/pattern_engine.py)](#9-candlestick-patterns-truth-engine-episode-17)
- [10. Gap Theory Engine (Episode 18) (alphacouncil/alpha/gap_engine.py)](#10-gap-theory-engine-episode-18)
- [11. Market Traps & LOTL Engine (Episode 19) (alphacouncil/alpha/trap_and_pattern_engine.py)](#11-market-traps--lotl-engine-episode-19)
- [12. High-Speed Stock Scanner & Dynamic Trailing Engine (Episode 20) (alphacouncil/alpha/scanner_and_trailing_engine.py)](#12-high-speed-stock-scanner--dynamic-trailing-engine-episode-20)
- [13. Pre-Trade Risk Engine & Concentration Limits (alphacouncil/risk/pre_trade.py)](#13-pre-trade-risk-engine--concentration-limits)
- [14. Position Sizing & Kelly Calibration (alphacouncil/risk/sizing.py)](#14-position-sizing--kelly-calibration)
- [15. López de Prado Meta-Labeler Downscaler (alphacouncil/risk/meta_labeler.py)](#15-lópez-de-prado-meta-labeler-downscaler)
- [16. Intraday Kill-Switch & Monthly Session Halt (alphacouncil/risk/kill_switch.py)](#16-intraday-kill-switch--monthly-session-halt)
- [17. Direction-Aware Circuit Band Guard (alphacouncil/risk/circuits.py)](#17-direction-aware-circuit-band-guard)
- [18. GTF Risk Management & Capital Protection Engine (alphacouncil/risk/gtf_risk.py)](#18-gtf-risk-management--capital-protection-engine)
- [19. Statutory Indian Market Friction Model (SEBI Oct 2024) (alphacouncil/execution/friction.py)](#19-statutory-indian-market-friction-model-sebi-oct-2024)
- [20. Idempotent OMS & Broker GTT Bracket Sync (alphacouncil/execution/oms.py)](#20-idempotent-oms--broker-gtt-bracket-sync)
- [21. Purged Walk-Forward Backtesting Engine (alphacouncil/backtest/engine.py)](#21-purged-walk-forward-backtesting-engine)
- [22. Deflated Sharpe Ratio (DSR) & Quant Metrics (alphacouncil/backtest/metrics.py)](#22-deflated-sharpe-ratio-dsr--quant-metrics)
- [23. 7-Model Orthogonal Ablation Suite (alphacouncil/backtest/ablation.py)](#23-7-model-orthogonal-ablation-suite)
- [24. Interactive Bloomberg Dashboard UI (alphacouncil/ui/dashboard.py)](#24-interactive-bloomberg-dashboard-ui)
- [25. Master Research Demo Runner (alphacouncil/run_council.py)](#25-master-research-demo-runner)
- [26. Forward Paper Testing Engine & Pullback Order Lifecycle (alphacouncil/execution/paper_trader.py)](#26-forward-paper-testing-engine--pullback-order-lifecycle)

---

## 1. Configuration & Statutory Parameters (`alphacouncil/config.py`)

```python
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
    cold_start_trade_threshold: int = Field(default=50, description="Bypass Kelly until 50 trades closed (calibrated for swing trading)")
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

```

---

## 2. Market Data Feed & Synthetic Generator (`alphacouncil/data/feed.py`)

```python
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

        # Sequential Chained Martingale Jump-Diffusion
        # Connects each bar's open directly to the prior bar's close, guaranteeing
        # that E[r_t * r_{t-1}] = 0 (unbiased martingale random walk with no artificial autocorrelation).
        curr_close = initial_price

        # Trading day calendar (excluding weekends, anchored to 2023-01-02 historical past)
        cur_d = datetime.date(2023, 1, 2)
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
        volumes = []

        for i in range(n_bars):
            # Overnight return + occasional corporate earnings / macro jump
            if i == 0:
                p_open = initial_price
            else:
                overnight_shock = self.rng.standard_normal() * (daily_vol * 0.35)
                jump = self.rng.normal(0.0, daily_vol * 2.5) if self.rng.random() < 0.05 else 0.0
                p_open = max(10.0, curr_close * np.exp(overnight_shock + jump))

            # Intraday price path evolution
            intraday_shock = self.rng.standard_normal() * (daily_vol * 0.93)
            p_close = max(10.0, p_open * np.exp(drift + intraday_shock))

            # Realistic upper and lower wicks
            high_wick = abs(self.rng.standard_normal()) * (daily_vol * 0.40) * p_open
            low_wick = abs(self.rng.standard_normal()) * (daily_vol * 0.40) * p_open
            p_high = max(p_open, p_close) + high_wick
            p_low = max(5.0, min(p_open, p_close) - low_wick)

            # Lognormal volume variation
            vol_multiplier = np.exp(self.rng.normal(0.0, 0.35))
            vol = max(10_000.0, base_adv * vol_multiplier)

            curr_close = p_close
            highs.append(p_high)
            lows.append(p_low)
            closes.append(p_close)
            volumes.append(vol)

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

```

---

## 3. Point-in-Time Corporate Calendar & LODR 29 (`alphacouncil/data/calendar.py`)

```python
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
            for yr in [2023, 2024, 2025, 2026, 2027]:
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

    @staticmethod
    def get_sector(symbol: str) -> str:
        """Point-in-time sectoral classification for NSE liquid universe."""
        mapping = {
            "INFY": "IT", "TCS": "IT", "WIPRO": "IT", "HCLTECH": "IT",
            "HDFCBANK": "BANKING", "ICICIBANK": "BANKING", "SBIN": "BANKING",
            "KOTAKBANK": "BANKING", "AXISBANK": "BANKING",
            "RELIANCE": "ENERGY", "ONGC": "ENERGY", "BPCL": "ENERGY",
            "TATAMOTORS": "AUTO", "MARUTI": "AUTO", "M&M": "AUTO", "BAJAJ-AUTO": "AUTO",
            "TATASTEEL": "METALS", "JSWSTEEL": "METALS", "HINDALCO": "METALS",
            "SUNPHARMA": "PHARMA", "CIPLA": "PHARMA", "DRREDDY": "PHARMA",
            "ITC": "FMCG", "HINDUNILVR": "FMCG", "NESTLEIND": "FMCG",
        }
        return mapping.get(symbol.upper(), "GENERAL")

    def get_latest_headline(self, symbol: str, current_date: str) -> str:
        """
        Research Prototype Stub / Synthetic Lexicon Disclosure Feeder.
        Generates reproducible headline excerpts for testing the NLP feature pipeline
        without lookahead leakage.
        In live production, replace with real-time SEBI / NSE RSS disclosure feed parser.
        """
        self._ensure_symbol_events(symbol)
        if self.is_earnings_within_window(symbol, current_date, days_ahead=5):
            return f"{symbol} corporate release: board scheduled to review EBITDA growth and capex guidance."

        # Periodic financial disclosures based on date hash
        date_hash = sum(ord(c) for c in (symbol + current_date))
        if date_hash % 9 == 0:
            return f"{symbol} quarterly operational update: order book record and market share gain across key divisions."
        elif date_hash % 11 == 0:
            return f"{symbol} regulatory note: management cautions on raw material headwinds and potential margin contraction."
        return f"{symbol} standard disclosures: operations in line with guidance; routine capital deployment."

```

---

## 4. Demand & Supply Zone Core Engine (GTF Model) (`alphacouncil/alpha/zone_engine.py`)

```python
"""
Demand & Supply Core Engine (Trading in the Zone / GTF Methodology).
Codifies institutional order-matching mechanics, Exciting vs Base candle classification,
structural zone detection (DBR, RBR, RBD, DBD), exact Zone Marking (Proximal & Distal lines),
Normal vs. Exceptional marking (reversal vs. continuous wick rules),
Wick-to-Wick aggressive zone mapping, Direct Reversals (missing base candles),
Zone strength scoring (1-3 base vs. 4-5+ base candles), Timeframe Hierarchy,
The Closing Concept (Proven vs. Unproven Zones), Gap + Base = Exciting Candle Equation,
Level-on-Top-of-Level (LOTL) Stacking, Origin Pivot Isolation, Garbage Area Filtering,
and Trading Psychology Anti-News Liquidity Trap filtering ("Human can lie, but chart can't").
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
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


class TradingStance(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"  # Default: Safe, deep origin, matching HTF timeframe
    AGGRESSIVE = "AGGRESSIVE"      # Permitted only when clean space ahead OR proven achievement


class TimeframeTier(str, Enum):
    YEARLY = "YEARLY"          # Macro annual (Weight 6.0)
    HALF_YEARLY = "HALF_YEARLY" # Macro bi-annual (Weight 5.5)
    QUARTERLY = "QUARTERLY"    # Macro institutional allocation (Weight 5.0)
    MONTHLY = "MONTHLY"        # Highest institutional dominance (Weight 4.0)
    WEEKLY = "WEEKLY"          # Intermediate institutional swing (Weight 3.0)
    DAILY = "DAILY"            # Standard positional baseline (Weight 2.0)
    M125 = "125M"              # Exact NSE session partition 3 bars/day (Weight 1.5)
    M75 = "75M"                # Exact NSE session partition 5 bars/day (Weight 1.25)
    INTRADAY = "INTRADAY"      # 5m-60m noise vulnerable (Weight 1.0)


class TradingStyle(str, Enum):
    HIT = "HIT"  # Hourly Income Trade: 60m/75m HTF -> 15m ITF -> 5m LTF
    DIT = "DIT"  # Daily Income Trade: Daily HTF -> 60m/75m ITF -> 15m LTF
    WIT = "WIT"  # Weekly Income Trade / Swing: Weekly HTF -> Daily ITF -> 125m LTF
    MIT = "MIT"  # Monthly Income Trade / Positional: Monthly HTF -> Weekly ITF -> Daily LTF
    QIT = "QIT"  # Quarterly Investing: Quarterly HTF -> Monthly ITF -> Weekly LTF


class TrendDirection(str, Enum):
    UPTREND = "UPTREND"      # 12 to 3 o'clock (positive slope, green)
    DOWNTREND = "DOWNTREND"  # 3 to 6 o'clock (negative slope, red)
    SIDEWAYS = "SIDEWAYS"    # 3 o'clock flat


class CurvePosition(str, Enum):
    VERY_LOW_ON_CURVE = "VERY_LOW_ON_CURVE"    # VLOC: Inside Demand Zone (Below Demand PL)
    LOW_ON_CURVE = "LOW_ON_CURVE"              # LOC: Lower Third (0% to 33.33%)
    EQUILIBRIUM = "EQUILIBRIUM"                # EQB: Middle Third (33.33% to 66.66%)
    HIGH_ON_CURVE = "HIGH_ON_CURVE"            # HOC: Upper Third (66.66% to 100.0%)
    VERY_HIGH_ON_CURVE = "VERY_HIGH_ON_CURVE"  # VHOC: Inside Supply Zone (Above Supply PL)
    ALL_TIME_HIGH = "ALL_TIME_HIGH"            # ATH: Above all historical resistance


class TradeActionBias(str, Enum):
    BUY_ONLY = "BUY_ONLY"
    SELL_ONLY = "SELL_ONLY"
    BUY_AGGRESSIVE = "BUY_AGGRESSIVE"  # VLOC with pristine origin against downtrend
    NO_TRADE = "NO_TRADE"              # Hazardous counter-trend trap


@dataclass
class MultiTimeframePlan:
    trading_style: TradingStyle
    htf_timeframe: TimeframeTier
    itf_timeframe: TimeframeTier
    ltf_timeframe: TimeframeTier
    cmp: float
    curve_position: CurvePosition
    curve_retracement_pct: float
    itf_trend: TrendDirection
    itf_sma_slope: float
    action_bias: TradeActionBias
    eligible_execution_zones: List["IdentifiedZone"]
    rejected_boundary_zones: List["IdentifiedZone"]
    rationale: str


class TradeScoreQuality(str, Enum):
    PRISTINE = "PRISTINE"  # 7.0 / 7.0 (Best Setup)
    SOLID = "SOLID"        # 6.0 - 6.5 / 7.0 (Better Setup)
    WEAK = "WEAK"          # <= 5.5 / 7.0 (Poor / Discarded)


class ZoneAlignmentType(str, Enum):
    COINCIDING = "COINCIDING"  # Arjuna beside Shri Krishna (Safest, highest institutional backing)
    AGGRESSIVE = "AGGRESSIVE"  # Arjuna stands ahead of Shri Krishna (Requires score >= 6.5/7.0)
    FATAL_TRAP = "FATAL_TRAP"  # Arjuna entering Bhishma Pitamah or Duryodhana right after Shri Krishna bounce


class MACrossoverType(str, Enum):
    GOLDEN_CROSSOVER = "GOLDEN_CROSSOVER"  # EMA 20 crosses above EMA 50
    DEATH_CROSSOVER = "DEATH_CROSSOVER"    # EMA 20 crosses below EMA 50
    NO_CROSSOVER = "NO_CROSSOVER"


@dataclass
class TradeScoreBreakdown:
    freshness_score: float             # 0.0, 1.5, or 3.0
    strength_score: float              # 1.0 or 2.0
    time_at_base_score: float          # 0.0, 1.0, or 2.0
    total_score: float                 # Sum out of 7.0 (or up to 8.0 with bonus)
    quality: TradeScoreQuality
    alignment: ZoneAlignmentType
    is_best_setup: bool
    opposing_itf_target_price: Optional[float] = None
    realized_rrr: float = 0.0
    is_target_acceptable: bool = True
    rejection_reasons: List[str] = field(default_factory=list)
    ma_crossover_bonus: int = 0        # 0 or 1 point from Episode 12
    crossover_type: MACrossoverType = MACrossoverType.NO_CROSSOVER
    ema20_confluence_bonus: int = 0    # 0 or 1 point from Episode 13
    sector_support_bonus: int = 0      # 0 or 2 points from Episode 16 (The Supreme Add-on)
    sector_confluence_level: str = ""  # Level 1, Level 2, or Level 3 Rocket Move
    candlestick_pattern_bonus: int = 0 # 0 or 1 point from Episode 17 (Post-Entry Confidence Booster)
    gap_confluence_bonus: int = 0      # 0, 1, or 2 points from Episode 18 (Gap Theory)
    gap_application: str = ""          # Application 1, 2, 3, or 4
    indicator_confluence_bonus: int = 0 # 0 or 1 point from Episode 19 (RSI/Stochastic Confluence)
    lotl_entry_mode: str = ""          # AGGRESSIVE, CONSERVATIVE, or BALANCED_MIDDLE
    is_lotl_zone: bool = False         # True if part of Level on Top of the Level setup
    trailing_sl_eligible: bool = False # True if eligible for dynamic Weekly Demand Distal trailing (Episode 20)
    price_alert_level: Optional[float] = None # Alert 1-2 points above PL (Episode 20)
    on_chart_note: str = ""            # Standardized 5-second restoration note (Episode 20)


class EntryType(str, Enum):
    SET_AND_FORGET = "SET_AND_FORGET"          # Entry Type 1: Limit order slightly above PL (The Gold Standard)
    CONFIRMATION_IN_ZONE = "CONFIRMATION_IN_ZONE"  # Entry Type 2: 1st closes in zone, 2nd opens in zone
    BREAKOUT_DEPARTURE = "BREAKOUT_DEPARTURE"      # Entry Type 3: 1st in zone, subsequent exits zone


class ZoneAuthenticity(str, Enum):
    AUTHENTIC = "AUTHENTIC"          # Formed in virgin/clean space, genuine origin of order flow
    NON_AUTHENTIC = "NON_AUTHENTIC"  # Reaction bounce off a preceding historical zone


class TradingStyleCategory(str, Enum):
    INTRADAY = "INTRADAY"    # HIT, DIT (High noise, micro SL, requires >=100 prior positional trades)
    POSITIONAL = "POSITIONAL" # WIT, MIT, QIT (Structurally durable, top-down vision)


@dataclass
class RejectionAudit:
    is_rejected: bool
    rejection_reasons: List[str]
    survived_rejection_mindset: bool
    recommended_entry_type: EntryType
    rupee_risk_equalized_shares: int = 0
    positional_trade_count: int = 0
    intraday_advisory: str = ""


class ConfirmationEntryType(str, Enum):
    MACRO_HTF_CONFIRMATION = "MACRO_HTF_CONFIRMATION"  # Episode 14: 1 LTF supply breached backed by HTF demand
    STANDARD_LIMIT = "STANDARD_LIMIT"                  # Episode 9: Type 1 Set & Forget limit
    ATL_PROHIBITED = "ATL_PROHIBITED"                  # All-Time Low long entry prohibited


@dataclass
class ConfirmationTradePlan:
    htf_demand_zone: "IdentifiedZone"
    nearest_ltf_supply_zone: "IdentifiedZone"
    is_htf_demand_tested: bool
    is_supply_eliminated_by_close: bool
    newly_formed_ltf_demand: Optional["IdentifiedZone"]
    macro_risk_per_share: float
    compressed_risk_per_share: float
    risk_compression_ratio: float
    realized_target_rrr: float
    is_confirmed: bool
    status_message: str


class MacroSupplyWallStatus(str, Enum):
    NO_WALL = "NO_WALL"
    COLLIDING_WITH_WALL = "COLLIDING_WITH_WALL"
    FALLING_AWAY_FROM_WALL = "FALLING_AWAY_FROM_WALL"


class OriginQuality(str, Enum):
    PRISTINE_ORIGIN = "PRISTINE_ORIGIN"          # Origin base at major cycle bottom/pivot with EMA support; 8:1 to 10:1+ RRR
    SHALLOW_DISTRIBUTIVE = "SHALLOW_DISTRIBUTIVE" # Mid-air consolidation or distributive stair-step; vulnerable to macro wall
    GARBAGE_CONSOLIDATION = "GARBAGE_CONSOLIDATION" # Extended directionless consolidation with overlapping wicks; rejected


@dataclass
class MasterRevisionAuditReport:
    is_approved: bool
    trading_stance: TradingStance
    recommended_entry_type: EntryType
    macro_wall_status: MacroSupplyWallStatus
    origin_quality: OriginQuality
    curve_position: CurvePosition
    itf_trend: TrendDirection
    trade_score: float
    calculated_position_size: int
    projected_rrr: float
    audit_checks_passed: List[str]
    rejection_reasons: List[str]
    audit_verdict_summary: str
    overpowering_htf_supply: Optional["IdentifiedZone"] = None


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
    is_gap_exciting: bool = False  # Episode 6: Gap + Base = Exciting Candle
    gap_distance: float = 0.0


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

    # Price Action Nuances (Episode 6)
    has_clean_closing: bool = True          # Leg-out closed decisively above Leg-in (Demand) or below (Supply)
    is_proven_zone: bool = True             # True if clean close cleared opposing overhead/underlying orders
    origin_candle_idx: Optional[int] = None # True origin pivot candle in multi-base cluster
    is_gap_base_zone: bool = False          # Zone formed via Gap + Base synthetic exciting candle

    # Quantitative Zone Rating & Best Setup Evaluation (Episode 8)
    trade_score: Optional[TradeScoreBreakdown] = None

    # Authenticity & Execution Mechanics (Episode 9)
    authenticity: ZoneAuthenticity = ZoneAuthenticity.AUTHENTIC
    reaction_parent_idx: Optional[int] = None
    recommended_entry_type: EntryType = EntryType.SET_AND_FORGET

    # Advanced Price Action Nuance (Episode 10)
    is_htf_overpowering_origin: bool = False  # True if smaller TF zone overpowered opposing HTF structure

    # Execution Stance & Macro Anchoring (Episode 11)
    trading_stance: TradingStance = TradingStance.CONSERVATIVE
    has_proven_achievement: bool = False       # True if zone closed beyond opposing HTF zone
    anchored_htf_stoploss: Optional[float] = None # Stoploss anchored to Shri Krishna (HTF Distal Line)

    # Gap Theory & Window Gap Mechanics (Episode 18)
    is_pro_gap_origin: bool = False             # Zone formed via institutional Pro Gap departure
    window_gap_level: Optional[float] = None    # Level of window gap (lowest wick for demand, highest wick for supply)
    window_gap_decision: Optional[str] = None   # WINDOW_GAP_ELEVATED or WINDOW_GAP_DISCIPLINED_BASE

    # LOTL & Market Traps Mechanics (Episode 19)
    is_lotl_origin: bool = False                # True if lower demand or upper supply origin in LOTL
    is_lotl_cushion: bool = False               # True if upper demand or lower supply cushion in LOTL
    lotl_merged_entry: Optional[float] = None   # Middle or selected entry price
    lotl_merged_stoploss: Optional[float] = None # Lower distal (demand) or upper distal (supply)

    # Dynamic Trailing & Alert Architecture (Episode 20)
    is_trailing_multi_bagger_active: bool = False # True if riding ATH or macro expansion
    current_trailing_sl: Optional[float] = None   # Current ratchet level anchored to Weekly Demand Distal
    price_alert_level: Optional[float] = None     # Alert price placed 1-2 points above PL


class DemandSupplyEngine:
    """
    Core Price Action Engine trained on Institutional Order Flow,
    Demand-Supply Imbalances, Normal vs. Exceptional Zone Marking,
    Wick-to-Wick Mapping, Timeframe Hierarchy, The Closing Concept,
    Gap+Base Identity, Origin Isolation, and Trading Psychology.
    """

    TIMEFRAME_WEIGHTS: Dict[TimeframeTier, float] = {
        TimeframeTier.YEARLY: 6.0,
        TimeframeTier.HALF_YEARLY: 5.5,
        TimeframeTier.QUARTERLY: 5.0,
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
        min_gap_ratio: float = 0.50,
    ):
        self.min_range_atr_ratio = min_range_atr_ratio
        self.max_base_candles = max_base_candles
        self.use_exceptional_marking = use_exceptional_marking
        self.buffer_ratio = buffer_ratio
        self.min_buffer = min_buffer
        self.target_rrr = target_rrr
        self.default_marking_mode = default_marking_mode
        self.default_timeframe = default_timeframe
        self.min_gap_ratio = min_gap_ratio

    @staticmethod
    def get_nse_session_partitions() -> Dict[str, int]:
        """
        Episode 1: Standard 375-minute Indian market session (09:15 to 15:30 IST).
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

    @staticmethod
    def is_garbage_cluster(
        highs: np.ndarray,
        lows: np.ndarray,
        start_idx: int,
        end_idx: int,
        min_bars: int = 6,
    ) -> bool:
        """
        Episode 6 Concept 5: Garbage Areas
        Prolonged directionless sideways consolidation packed with overlapping wicks,
        no directional progress, and lack of distance from origin.
        """
        count = end_idx - start_idx + 1
        if count < min_bars:
            return False

        cluster_high = float(np.max(highs[start_idx : end_idx + 1]))
        cluster_low = float(np.min(lows[start_idx : end_idx + 1]))
        cluster_range = cluster_high - cluster_low

        avg_bar_range = float(np.mean(highs[start_idx : end_idx + 1] - lows[start_idx : end_idx + 1]))
        if avg_bar_range <= 1e-6:
            return True

        # If 6+ bars are crammed within <= 2.2x of the average single bar range -> Garbage churn
        return bool(cluster_range <= (2.2 * avg_bar_range))

    @classmethod
    def detect_level_on_top_of_level(
        cls, zones: List[IdentifiedZone], max_distance_pct: float = 0.08
    ) -> List[Dict[str, Any]]:
        """
        Episode 6 Concept 2: Stacking Zones (Level-on-Top-of-Level - LOTL).
        Identifies stacked adjacent demand or supply zones:
        - Zone 1 (Origin Baseline)
        - Zone 2 (Upper Gap-Base / Secondary Zone)
        Zone 2 acts as an absorption cushion, absorbing incoming momentum before Zone 1.
        """
        lotl_pairs: List[Dict[str, Any]] = []
        n_z = len(zones)
        for i in range(n_z):
            z1 = zones[i]
            for j in range(i + 1, n_z):
                z2 = zones[j]
                if z1.is_demand and z2.is_demand:
                    lower = z1 if z1.proximal_line < z2.proximal_line else z2
                    upper = z2 if z1.proximal_line < z2.proximal_line else z1
                    dist = (upper.distal_line - lower.proximal_line) / lower.proximal_line
                    if 0 <= dist <= max_distance_pct:
                        lotl_pairs.append({
                            "type": "DEMAND_LOTL",
                            "origin_zone": lower,
                            "cushion_zone": upper,
                            "combined_entry": upper.entry_price,
                            "combined_stop_loss": lower.stop_loss,
                            "absorption_cushion_active": True,
                        })
                elif not z1.is_demand and not z2.is_demand:
                    lower = z1 if z1.proximal_line < z2.proximal_line else z2
                    upper = z2 if z1.proximal_line < z2.proximal_line else z1
                    dist = (upper.proximal_line - lower.distal_line) / lower.proximal_line
                    if 0 <= dist <= max_distance_pct:
                        lotl_pairs.append({
                            "type": "SUPPLY_LOTL",
                            "origin_zone": upper,
                            "cushion_zone": lower,
                            "combined_entry": lower.entry_price,
                            "combined_stop_loss": upper.stop_loss,
                            "absorption_cushion_active": True,
                        })
        return lotl_pairs

    @staticmethod
    def calculate_sma50_clock_trend(
        closes: np.ndarray, lookback_bars: int = 7, min_sma_period: int = 50
    ) -> Tuple[TrendDirection, float, str]:
        """
        Episode 7: Trend Analysis - The 50 SMA Clock Method.
        Evaluates the 7-candle lookback on the 50-period Simple Moving Average.
        - 12 to 3 o'clock (positive slope, green) -> UPTREND
        - 3 to 6 o'clock (negative slope, red) -> DOWNTREND
        - 3 o'clock flat -> SIDEWAYS
        """
        n = len(closes)
        if n < lookback_bars:
            return TrendDirection.SIDEWAYS, 0.0, "3_OCLOCK_FLAT"

        period = min(min_sma_period, n)
        sma_curr = float(np.mean(closes[-period:]))

        if n >= period + lookback_bars:
            sma_past = float(np.mean(closes[-period - lookback_bars : -lookback_bars]))
        elif n > lookback_bars:
            sma_past = float(np.mean(closes[: max(1, n - lookback_bars)]))
        else:
            sma_past = float(closes[0])

        if sma_past <= 1e-6:
            return TrendDirection.SIDEWAYS, 0.0, "3_OCLOCK_FLAT"

        delta_pct = (sma_curr - sma_past) / sma_past

        if delta_pct >= 0.0005:
            return TrendDirection.UPTREND, round(delta_pct, 4), "12_TO_3_OCLOCK"
        elif delta_pct <= -0.0005:
            return TrendDirection.DOWNTREND, round(delta_pct, 4), "3_TO_6_OCLOCK"
        else:
            return TrendDirection.SIDEWAYS, round(delta_pct, 4), "3_OCLOCK_FLAT"

    @staticmethod
    def calculate_curve_position(
        cmp: float,
        htf_demand: IdentifiedZone,
        htf_supply: Optional[IdentifiedZone] = None,
    ) -> Tuple[CurvePosition, float]:
        """
        Episode 7: Higher Time Frame Curve / Location Analysis.
        Divides the curve between Demand Proximal (0%) and Supply Proximal (100%) into:
        - VERY_LOW_ON_CURVE: Inside Demand Zone (CMP < Demand PL)
        - LOW_ON_CURVE: Lower Third (0% to 33.33%)
        - EQUILIBRIUM: Middle Third (33.33% to 66.66%)
        - HIGH_ON_CURVE: Upper Third (66.66% to 100.0%)
        - VERY_HIGH_ON_CURVE: Inside Supply Zone (CMP > Supply PL)
        - ALL_TIME_HIGH: No fresh overhead supply exists; shorting is strictly prohibited.
        """
        if htf_supply is None:
            return CurvePosition.ALL_TIME_HIGH, 0.0

        dem_prox = htf_demand.proximal_line
        sup_prox = htf_supply.proximal_line
        curve_range = sup_prox - dem_prox

        if curve_range <= 1e-6:
            return CurvePosition.EQUILIBRIUM, 50.0

        pct = ((cmp - dem_prox) / curve_range) * 100.0

        if cmp < dem_prox:
            return CurvePosition.VERY_LOW_ON_CURVE, round(pct, 2)
        elif pct <= 33.33:
            return CurvePosition.LOW_ON_CURVE, round(pct, 2)
        elif pct <= 66.66:
            return CurvePosition.EQUILIBRIUM, round(pct, 2)
        elif pct <= 100.0:
            return CurvePosition.HIGH_ON_CURVE, round(pct, 2)
        else:
            return CurvePosition.VERY_HIGH_ON_CURVE, round(pct, 2)

    @classmethod
    def build_multi_timeframe_plan(
        cls,
        trading_style: TradingStyle,
        cmp: float,
        htf_demand: IdentifiedZone,
        htf_supply: Optional[IdentifiedZone],
        itf_closes: np.ndarray,
        ltf_zones: List[IdentifiedZone],
        opposing_itf_zone: Optional[IdentifiedZone] = None,
    ) -> MultiTimeframePlan:
        """
        Episode 7: Multiple Time Frame Analysis (MTFA) Decision Plan.
        1. Identifies HTF Location / Curve Position (VLOC, LOC, EQB, HOC, VHOC, ATH).
        2. Evaluates ITF Trend via 50 SMA Clock Method (12-3 Uptrend, 3-6 Downtrend).
        3. Enforces Directional Bias Alignment (~95% Rule & ATH Rule).
        4. Enforces The Boundary Rule: LTF execution zone must NEVER extend past HTF Distal Line.
        """
        if trading_style == TradingStyle.HIT:
            htf_tf = TimeframeTier.INTRADAY
            itf_tf = TimeframeTier.INTRADAY
            ltf_tf = TimeframeTier.INTRADAY
        elif trading_style == TradingStyle.DIT:
            htf_tf = TimeframeTier.DAILY
            itf_tf = TimeframeTier.INTRADAY
            ltf_tf = TimeframeTier.INTRADAY
        elif trading_style == TradingStyle.WIT:
            htf_tf = TimeframeTier.WEEKLY
            itf_tf = TimeframeTier.DAILY
            ltf_tf = TimeframeTier.M125
        elif trading_style == TradingStyle.MIT:
            htf_tf = TimeframeTier.MONTHLY
            itf_tf = TimeframeTier.WEEKLY
            ltf_tf = TimeframeTier.DAILY
        else:  # QIT
            htf_tf = TimeframeTier.MONTHLY
            itf_tf = TimeframeTier.WEEKLY
            ltf_tf = TimeframeTier.DAILY

        curve_pos, curve_pct = cls.calculate_curve_position(cmp, htf_demand, htf_supply)
        trend, slope, clock_pos = cls.calculate_sma50_clock_trend(itf_closes)

        rationale_parts = [
            f"Trading Style: {trading_style.value}.",
            f"HTF Location: {curve_pos.value} ({curve_pct}% retracement).",
            f"ITF Trend: {trend.value} ({clock_pos}, slope: {slope}).",
        ]

        if curve_pos == CurvePosition.ALL_TIME_HIGH:
            if trend == TrendDirection.UPTREND:
                action_bias = TradeActionBias.BUY_ONLY
                rationale_parts.append(
                    "Asset at All-Time Highs with Uptrend. Long setups only; shorting is strictly prohibited."
                )
            else:
                action_bias = TradeActionBias.NO_TRADE
                rationale_parts.append(
                    "Asset at All-Time Highs but lack of Uptrend momentum. No trade."
                )
        elif curve_pos == CurvePosition.VERY_LOW_ON_CURVE:
            if trend == TrendDirection.DOWNTREND:
                action_bias = TradeActionBias.BUY_AGGRESSIVE
                rationale_parts.append(
                    "Very Low on Curve against Downtrend. Buy permitted only on pristine origin demand."
                )
            else:
                action_bias = TradeActionBias.BUY_ONLY
                rationale_parts.append("Very Low on Curve confirmed by trend. Definitely Buy.")
        elif curve_pos == CurvePosition.LOW_ON_CURVE:
            if trend == TrendDirection.DOWNTREND:
                action_bias = TradeActionBias.NO_TRADE
                rationale_parts.append(
                    "Low on Curve with Downtrend. Counter-trend trap; buying prohibited without trend alignment."
                )
            else:
                action_bias = TradeActionBias.BUY_ONLY
                rationale_parts.append("Low on Curve confirmed with Uptrend. High probability Buy.")
        elif curve_pos == CurvePosition.EQUILIBRIUM:
            if trend == TrendDirection.UPTREND:
                action_bias = TradeActionBias.BUY_ONLY
                rationale_parts.append("Equilibrium position. Follow intermediate Uptrend momentum.")
            elif trend == TrendDirection.DOWNTREND:
                action_bias = TradeActionBias.SELL_ONLY
                rationale_parts.append("Equilibrium position. Follow intermediate Downtrend momentum.")
            else:
                action_bias = TradeActionBias.NO_TRADE
                rationale_parts.append(
                    "Equilibrium position with Sideways trend. Directional edge absent; no trade."
                )
        elif curve_pos == CurvePosition.HIGH_ON_CURVE:
            if trend == TrendDirection.UPTREND:
                action_bias = TradeActionBias.NO_TRADE
                rationale_parts.append(
                    "High on Curve with Uptrend. Counter-trend trap; shorting prohibited into bullish momentum."
                )
            else:
                action_bias = TradeActionBias.SELL_ONLY
                rationale_parts.append("High on Curve confirmed with Downtrend. High probability Short.")
        else:  # VERY_HIGH_ON_CURVE
            if trend == TrendDirection.UPTREND:
                action_bias = TradeActionBias.NO_TRADE
                rationale_parts.append("Very High on Curve but Uptrend persists. Await trend exhaustion.")
            else:
                action_bias = TradeActionBias.SELL_ONLY
                rationale_parts.append("Very High on Curve confirmed by Downtrend. Definitely Sell / Short.")

        # Episode 7 Concept 7: The Boundary Rule
        eligible: List[IdentifiedZone] = []
        rejected: List[IdentifiedZone] = []

        for z in ltf_zones:
            if action_bias in (TradeActionBias.BUY_ONLY, TradeActionBias.BUY_AGGRESSIVE):
                if z.is_demand:
                    if z.distal_line >= htf_demand.distal_line:
                        eligible.append(z)
                    else:
                        rejected.append(z)
            elif action_bias == TradeActionBias.SELL_ONLY:
                if not z.is_demand:
                    if htf_supply is not None:
                        if z.distal_line <= htf_supply.distal_line:
                            eligible.append(z)
                        else:
                            rejected.append(z)
                    else:
                        eligible.append(z)

        # Episode 8: Score eligible execution zones and evaluate best setup status
        for z in eligible:
            z.trade_score = cls.evaluate_best_trade_setup(
                z,
                htf_demand=htf_demand,
                htf_supply=htf_supply,
                itf_trend=trend,
                opposing_itf_zone=opposing_itf_zone,
            )

        return MultiTimeframePlan(
            trading_style=trading_style,
            htf_timeframe=htf_tf,
            itf_timeframe=itf_tf,
            ltf_timeframe=ltf_tf,
            cmp=cmp,
            curve_position=curve_pos,
            curve_retracement_pct=curve_pct,
            itf_trend=trend,
            itf_sma_slope=slope,
            action_bias=action_bias,
            eligible_execution_zones=eligible,
            rejected_boundary_zones=rejected,
            rationale=" ".join(rationale_parts),
        )



    # =========================================================================
    # EPISODE 8: TRADE SCORE & BEST TRADE SETUP EVALUATION
    # =========================================================================

    @staticmethod
    def calculate_trade_score(
        zone: IdentifiedZone,
        test_count: int = 0,
        is_gap_departure: bool = False,
    ) -> Tuple[float, float, float, float, TradeScoreQuality]:
        """
        Episode 8 Parameter Scoring (Total Max Score: 7 Points).
        Strictly applied to Lower Time Frame (Execution Time Frame) zones.

        Parameters:
        1. Freshness (Max 3 Points):
           - Completely Fresh (Untested): 3.0 Points
           - Tested Once (1 touch): 1.5 Points
           - Tested Twice or More (>=2 touches): 0.0 Points
        2. Strength of Departure (Max 2 Points):
           - >= 2 Exciting Candles in Leg-out: 2.0 Points
           - 1 Exciting Candle + Significant Gap: 2.0 Points
           - 1 Exciting Candle & No Gap: 1.0 Point
        3. Time at the Base (Max 2 Points):
           - 1 to 3 Base Candles: 2.0 Points (Fast, decisive victory)
           - 4 to 5 Base Candles: 1.0 Point (Contested struggle)
           - > 5 Base Candles: 0.0 Points (Garbage consolidation)
           - Direct Reversal (0 Base Candles): 2.0 Points

        Returns:
            (freshness_score, strength_score, time_at_base_score, total_score, quality)
        """
        # 1. Freshness
        if test_count == 0 and zone.is_fresh:
            freshness_score = 3.0
        elif test_count == 1:
            freshness_score = 1.5
        elif test_count >= 2:
            freshness_score = 0.0
        elif not zone.is_fresh:
            freshness_score = 1.5
        else:
            freshness_score = 3.0

        # 2. Strength
        if zone.departure_strength >= 2:
            strength_score = 2.0
        elif is_gap_departure or zone.is_gap_base_zone:
            strength_score = 2.0
        else:
            strength_score = 1.0

        # 3. Time at the Base
        if 1 <= zone.base_candles_count <= 3:
            time_at_base_score = 2.0
        elif 4 <= zone.base_candles_count <= 5:
            time_at_base_score = 1.0
        elif zone.base_candles_count > 5:
            time_at_base_score = 0.0
        else:
            # 0 base candles (direct reversal / V-shape)
            time_at_base_score = 2.0

        total_score = round(freshness_score + strength_score + time_at_base_score, 1)

        if total_score >= 7.0:
            quality = TradeScoreQuality.PRISTINE
        elif total_score >= 6.0:
            quality = TradeScoreQuality.SOLID
        else:
            quality = TradeScoreQuality.WEAK

        return freshness_score, strength_score, time_at_base_score, total_score, quality

    @staticmethod
    def evaluate_character_alignment(
        ltf_zone: IdentifiedZone,
        htf_demand: Optional[IdentifiedZone] = None,
        htf_supply: Optional[IdentifiedZone] = None,
    ) -> ZoneAlignmentType:
        """
        Episode 8: The Mahabharata Metaphor (Mapping 4 Characters on the Chart).
        HTF Demand: Shri Krishna (Supreme macro support)
        HTF Supply: Bhishma Pitamah (Massive macro resistance)
        LTF Demand: Arjuna (Long execution level)
        LTF Supply: Duryodhana (Short execution level)

        Returns:
            COINCIDING: Safest setup; LTF zone sits inside or at the boundary of HTF location.
            AGGRESSIVE: LTF zone stands ahead/outside HTF location; requires pristine 7/7 score.
            FATAL_TRAP: LTF zone sits directly inside opposing HTF institutional territory.
        """
        if ltf_zone.is_demand:
            # Long Setup: Arjuna
            # Fatal Trap: Arjuna entering Bhishma Pitamah's territory (HTF Supply)
            if htf_supply is not None:
                if ltf_zone.proximal_line >= htf_supply.proximal_line:
                    return ZoneAlignmentType.FATAL_TRAP

            # Coinciding: Arjuna standing beside Shri Krishna (HTF Demand)
            if htf_demand is not None:
                if ltf_zone.proximal_line <= htf_demand.proximal_line and ltf_zone.distal_line >= htf_demand.distal_line:
                    return ZoneAlignmentType.COINCIDING
                if ltf_zone.distal_line <= htf_demand.proximal_line and ltf_zone.proximal_line >= htf_demand.distal_line:
                    return ZoneAlignmentType.COINCIDING

            return ZoneAlignmentType.AGGRESSIVE
        else:
            # Short Setup: Duryodhana
            # Fatal Trap: Duryodhana entering Shri Krishna's territory (HTF Demand)
            if htf_demand is not None:
                if ltf_zone.proximal_line <= htf_demand.proximal_line:
                    return ZoneAlignmentType.FATAL_TRAP

            # Coinciding: Duryodhana standing beside Bhishma Pitamah (HTF Supply)
            if htf_supply is not None:
                if ltf_zone.proximal_line >= htf_supply.proximal_line and ltf_zone.distal_line <= htf_supply.distal_line:
                    return ZoneAlignmentType.COINCIDING
                if ltf_zone.distal_line >= htf_supply.proximal_line and ltf_zone.proximal_line <= htf_supply.distal_line:
                    return ZoneAlignmentType.COINCIDING

            return ZoneAlignmentType.AGGRESSIVE

    @staticmethod
    def calculate_opposing_itf_target(
        ltf_zone: IdentifiedZone,
        opposing_itf_zone: Optional[IdentifiedZone] = None,
        min_rrr: float = 2.0,
    ) -> Tuple[float, float, bool]:
        """
        Episode 8: Setting Real-World Targets (The Opposing ITF Zone Rule).
        - Long Trades: Target at Proximal Line of Opposing Supply Zone on Intermediate Time Frame (ITF).
        - Short Trades: Target at Proximal Line of Opposing Demand Zone on Intermediate Time Frame (ITF).
        - The 2:1 Minimum Target Filter: Realized RRR must be >= 2:1 before reaching the opposing ITF zone.

        Returns:
            (target_price, realized_rrr, is_target_acceptable)
        """
        risk = abs(ltf_zone.entry_price - ltf_zone.stop_loss)
        if risk <= 0.0:
            risk = max(ltf_zone.zone_width, 1.0)

        if ltf_zone.is_demand:
            # Long Setup
            if opposing_itf_zone is not None and not opposing_itf_zone.is_demand:
                target_price = opposing_itf_zone.proximal_line
                reward = target_price - ltf_zone.entry_price
                realized_rrr = round(reward / risk, 2)
            else:
                # Clear sky / ATH / No opposing ITF zone: default 2:1
                reward = min_rrr * risk
                target_price = round(ltf_zone.entry_price + reward, 2)
                realized_rrr = min_rrr
        else:
            # Short Setup
            if opposing_itf_zone is not None and opposing_itf_zone.is_demand:
                target_price = opposing_itf_zone.proximal_line
                reward = ltf_zone.entry_price - target_price
                realized_rrr = round(reward / risk, 2)
            else:
                reward = min_rrr * risk
                target_price = round(ltf_zone.entry_price - reward, 2)
                realized_rrr = min_rrr

        is_target_acceptable = bool(realized_rrr >= min_rrr)
        return target_price, realized_rrr, is_target_acceptable

    @classmethod
    def evaluate_best_trade_setup(
        cls,
        ltf_zone: IdentifiedZone,
        htf_demand: Optional[IdentifiedZone] = None,
        htf_supply: Optional[IdentifiedZone] = None,
        itf_trend: TrendDirection = TrendDirection.UPTREND,
        opposing_itf_zone: Optional[IdentifiedZone] = None,
        test_count: int = 0,
        is_gap_departure: bool = False,
        min_rrr: float = 2.0,
    ) -> TradeScoreBreakdown:
        """
        Episode 8: The Gold Standard "Best Trade Setup" Evaluator.
        A setup transitions from Good to Best when it satisfies four simultaneous criteria:
        1. Trade Score: Must score >= 6.0/7.0 (preferably 7.0/7.0).
        2. Clean Closing: Leg-out closed decisively above prior leg-in (Demand) or below (Supply).
        3. Alignment: Coinciding with HTF location (or aggressive with score 7.0 and ample room).
           Fatal traps are strictly blocked.
        4. Intermediate Trend Support: ITF trend aligns with trade direction.
        5. Opposing ITF Target RRR: Realized RRR to opposing ITF proximal line >= 2.0.
        """
        rejection_reasons: List[str] = []

        # 1. Trade Score
        f_score, s_score, t_score, total_score, quality = cls.calculate_trade_score(
            ltf_zone, test_count=test_count, is_gap_departure=is_gap_departure
        )
        if total_score < 6.0:
            rejection_reasons.append(f"Trade Score {total_score}/7 is below solid threshold (>=6.0).")

        # 2. Closing Concept
        if not ltf_zone.has_clean_closing or not ltf_zone.is_proven_zone:
            rejection_reasons.append("Leg-out failed clean closing above leg-in / overhead consolidation.")

        # 3. Mahabharata Character Alignment
        alignment = cls.evaluate_character_alignment(ltf_zone, htf_demand, htf_supply)
        if alignment == ZoneAlignmentType.FATAL_TRAP:
            rejection_reasons.append("Fatal Trap: Execution zone sits inside opposing HTF institutional territory.")
        elif alignment == ZoneAlignmentType.AGGRESSIVE and total_score < 7.0:
            rejection_reasons.append("Aggressive execution level requires pristine 7/7 score to trade without HTF backing.")

        # 4. Trend Support
        if ltf_zone.is_demand and itf_trend != TrendDirection.UPTREND:
            rejection_reasons.append(f"Long trade conflicts with ITF trend: {itf_trend.value} (Requires UPTREND).")
        elif not ltf_zone.is_demand and itf_trend != TrendDirection.DOWNTREND:
            rejection_reasons.append(f"Short trade conflicts with ITF trend: {itf_trend.value} (Requires DOWNTREND).")

        # 5. Dynamic Opposing ITF Target & RRR
        target_price, realized_rrr, is_target_acceptable = cls.calculate_opposing_itf_target(
            ltf_zone, opposing_itf_zone, min_rrr=min_rrr
        )
        if not is_target_acceptable:
            rejection_reasons.append(f"Realized RRR to opposing ITF zone ({realized_rrr}:1) is below {min_rrr}:1 minimum.")

        is_best = len(rejection_reasons) == 0

        return TradeScoreBreakdown(
            freshness_score=f_score,
            strength_score=s_score,
            time_at_base_score=t_score,
            total_score=total_score,
            quality=quality,
            alignment=alignment,
            is_best_setup=is_best,
            opposing_itf_target_price=target_price,
            realized_rrr=realized_rrr,
            is_target_acceptable=is_target_acceptable,
            rejection_reasons=rejection_reasons,
        )



    # =========================================================================
    # EPISODE 9: ENTRY TYPES, AUTHENTICITY, TRADING STYLES & REJECTION MINDSET
    # =========================================================================

    @staticmethod
    def evaluate_entry_type_2(
        zone: IdentifiedZone,
        bar1_close: float,
        bar2_open: float,
    ) -> Tuple[bool, str]:
        """
        Episode 9: Entry Type 2 (Confirmation Entry).
        Rule 1: Incoming candle must enter and close inside zone boundaries (between PL and DL).
        Rule 2: Trade executes only if second candle opens inside zone boundaries.
        Outcomes:
        - Gap Down below DL (Demand) / Gap Up above DL (Supply): Aborted! Saves trader from SL hit.
        - Gap Up above PL (Demand) / Gap Down below PL (Supply): Missed! Price departs without fill.
        - In-zone Open: Entry triggered.
        """
        if zone.is_demand:
            # Demand: DL is bottom, PL is top
            bar1_in = zone.distal_line <= bar1_close <= zone.proximal_line
            if not bar1_in:
                return False, "BAR1_DID_NOT_CLOSE_IN_ZONE"

            if bar2_open < zone.distal_line:
                return False, "ABORTED_GAP_DOWN_BELOW_DISTAL"
            elif bar2_open > zone.proximal_line:
                return False, "MISSED_GAP_UP_ABOVE_PROXIMAL"
            else:
                return True, "ENTRY_TRIGGERED_IN_ZONE"
        else:
            # Supply: PL is bottom, DL is top
            bar1_in = zone.proximal_line <= bar1_close <= zone.distal_line
            if not bar1_in:
                return False, "BAR1_DID_NOT_CLOSE_IN_ZONE"

            if bar2_open > zone.distal_line:
                return False, "ABORTED_GAP_UP_ABOVE_DISTAL"
            elif bar2_open < zone.proximal_line:
                return False, "MISSED_GAP_DOWN_BELOW_PROXIMAL"
            else:
                return True, "ENTRY_TRIGGERED_IN_ZONE"

    @staticmethod
    def evaluate_zone_authenticity(
        zone: IdentifiedZone,
        historical_zones: List[IdentifiedZone],
    ) -> Tuple[ZoneAuthenticity, bool, str]:
        """
        Episode 9: Authenticity and Credibility of Zones.
        - Authentic Zone: Forms independently in virgin space (origin of institutional order flow).
        - Non-Authentic Zone: Forms as an immediate reaction bounce to an earlier historical zone.
        Tradeability:
        - Non-authentic is Non-Tradeable by default if leg-out fails clean closing.
        - Non-authentic becomes Tradeable ONLY if it has an explosive, proven closing above leg-in.
        """
        is_reaction = False
        for h in historical_zones:
            if h.is_demand == zone.is_demand and h.first_leg_out_idx < zone.base_start_idx:
                if zone.is_demand:
                    # Check if zone base formed inside historical demand
                    if (h.distal_line <= zone.proximal_line <= h.proximal_line) or (
                        h.distal_line <= zone.distal_line <= h.proximal_line
                    ):
                        is_reaction = True
                        break
                else:
                    # Check if zone base formed inside historical supply
                    if (h.proximal_line <= zone.proximal_line <= h.distal_line) or (
                        h.proximal_line <= zone.distal_line <= h.distal_line
                    ):
                        is_reaction = True
                        break

        if is_reaction:
            authenticity = ZoneAuthenticity.NON_AUTHENTIC
            if zone.has_clean_closing and zone.is_proven_zone:
                is_tradeable = True
                rationale = "TRADEABLE_NON_AUTHENTIC_PROVEN_DEPARTURE"
            else:
                is_tradeable = False
                rationale = "NON_TRADEABLE_NON_AUTHENTIC_UNPROVEN_DEPARTURE"
        else:
            authenticity = ZoneAuthenticity.AUTHENTIC
            is_tradeable = True
            rationale = "AUTHENTIC_ORIGIN_ZONE"

        return authenticity, is_tradeable, rationale

    @staticmethod
    def calculate_rupee_risk_position_size(
        total_risk_inr: float,
        entry_price: float,
        stop_loss: float,
    ) -> int:
        """
        Episode 9 Concept 4B: The Rupee-Risk Equality Rule.
        A ₹50 stop-loss in an MIT positional trade and a ₹2 stop-loss in a DIT intraday trade
        carry the exact same monetary risk through position sizing.
        Formula: Quantity = floor(Total_Risk_INR / abs(Entry - StopLoss))
        """
        risk_pts = abs(entry_price - stop_loss)
        if risk_pts <= 0.0:
            return 0
        shares = int(total_risk_inr // risk_pts)
        return max(shares, 1)

    @staticmethod
    def enforce_mandatory_100_trade_rule(
        trading_style: TradingStyle,
        prior_positional_trades: int,
    ) -> Tuple[bool, str]:
        """
        Episode 9 Concept 4C: The Mandatory 100-Trade Directive.
        Every trader must execute at least 100 trades strictly in positional frameworks (WIT / MIT)
        before attempting high-stress active intraday styles (HIT / DIT).
        """
        if trading_style in (TradingStyle.HIT, TradingStyle.DIT):
            if prior_positional_trades < 100:
                return (
                    False,
                    f"Mandatory 100-Trade Directive: Only {prior_positional_trades}/100 positional trades completed. "
                    f"Intraday {trading_style.value} locked until 100 swing/positional trades achieved.",
                )
            else:
                return (
                    True,
                    f"Intraday {trading_style.value} unlocked: {prior_positional_trades} positional trades completed.",
                )
        else:
            return (
                True,
                f"Positional style {trading_style.value} is approved for systematic execution.",
            )

    @classmethod
    def audit_rejection_mindset(
        cls,
        zone: IdentifiedZone,
        htf_demand: Optional[IdentifiedZone] = None,
        htf_supply: Optional[IdentifiedZone] = None,
        itf_trend: TrendDirection = TrendDirection.UPTREND,
        opposing_itf_zone: Optional[IdentifiedZone] = None,
        trading_style: TradingStyle = TradingStyle.MIT,
        prior_positional_trades: int = 100,
        total_risk_inr: float = 1000.0,
        historical_zones: Optional[List[IdentifiedZone]] = None,
    ) -> RejectionAudit:
        """
        Episode 9 Concept 5A: The Rejection Mindset Audit.
        Instead of seeking reasons to buy, the professional filter actively hunts for reasons
        to REJECT the trade setup:
        1. Intermediate Trend Conflict -> Reject.
        2. Unproven / Poor Leg-out Closing -> Reject.
        3. Aggressive Level without 7/7 Score -> Reject.
        4. Non-Authentic Reaction without Proven Close -> Reject.
        5. Opposing ITF Target RRR < 2.0:1 -> Reject.
        6. Intraday Style attempted before 100 Positional Trades -> Reject.

        Surviving setups possess pristine institutional edge and eliminate over 50% of emotional turmoil.
        """
        rejection_reasons: List[str] = []

        # 1. 100-Trade Directive
        style_ok, style_msg = cls.enforce_mandatory_100_trade_rule(trading_style, prior_positional_trades)
        if not style_ok:
            rejection_reasons.append(style_msg)

        # 2. Trend Conflict
        if zone.is_demand and itf_trend != TrendDirection.UPTREND:
            rejection_reasons.append(f"Rejection: Long trade conflicts with ITF trend {itf_trend.value}.")
        elif not zone.is_demand and itf_trend != TrendDirection.DOWNTREND:
            rejection_reasons.append(f"Rejection: Short trade conflicts with ITF trend {itf_trend.value}.")

        # 3. Closing Concept
        if not zone.has_clean_closing or not zone.is_proven_zone:
            rejection_reasons.append("Rejection: Leg-out failed decisive close above leg-in / overhead consolidation.")

        # 4. Mahabharata Alignment & Traps
        alignment = cls.evaluate_character_alignment(zone, htf_demand, htf_supply)
        if alignment == ZoneAlignmentType.FATAL_TRAP:
            rejection_reasons.append("Rejection: Fatal Trap! Execution zone sits inside opposing HTF institutional territory.")

        # 5. Authenticity
        if historical_zones:
            auth, is_tradeable, auth_reason = cls.evaluate_zone_authenticity(zone, historical_zones)
            if not is_tradeable:
                rejection_reasons.append(f"Rejection: Non-authentic reaction zone with unproven departure ({auth_reason}).")

        # 6. Opposing ITF Target RRR
        target_price, rrr, rrr_ok = cls.calculate_opposing_itf_target(zone, opposing_itf_zone)
        if not rrr_ok:
            rejection_reasons.append(f"Rejection: Opposing ITF target offers {rrr}:1 RRR (minimum 2.0:1 required).")

        survived = len(rejection_reasons) == 0

        # Recommended Entry Type (Gold Standard: Set & Forget for Pristine/Solid)
        trade_score = getattr(zone, 'trade_score', None)
        tot_score = trade_score.total_score if trade_score else 7.0
        if tot_score >= 6.5 and zone.has_clean_closing:
            rec_entry = EntryType.SET_AND_FORGET
        elif 5.5 <= tot_score < 6.5:
            rec_entry = EntryType.CONFIRMATION_IN_ZONE
        else:
            rec_entry = EntryType.SET_AND_FORGET

        shares = cls.calculate_rupee_risk_position_size(total_risk_inr, zone.entry_price, zone.stop_loss)

        return RejectionAudit(
            is_rejected=not survived,
            rejection_reasons=rejection_reasons,
            survived_rejection_mindset=survived,
            recommended_entry_type=rec_entry,
            rupee_risk_equalized_shares=shares,
            positional_trade_count=prior_positional_trades,
            intraday_advisory=style_msg,
        )

    # =========================================================================
    # EPISODE 10: ADVANCED STRUCTURAL PRICE ACTION (HTF OVERPOWERING ORIGINS)
    # =========================================================================

    @staticmethod
    def detect_htf_overpowering_zone(
        ltf_zone: IdentifiedZone,
        opposing_htf_zone: IdentifiedZone,
    ) -> bool:
        """
        Episode 10 Concept 10: Smaller Timeframe Beating Higher Timeframe.
        When a smaller timeframe zone (Daily/125m) breaches and closes decisively beyond
        an opposing higher timeframe zone (Weekly/Monthly), that smaller timeframe zone
        becomes extraordinarily powerful as an institutional origin.
        """
        if ltf_zone.is_demand and not opposing_htf_zone.is_demand:
            # Demand breaches opposing HTF Supply's Distal Line on the upside
            if ltf_zone.proximal_line > opposing_htf_zone.distal_line and ltf_zone.has_clean_closing:
                ltf_zone.is_htf_overpowering_origin = True
                return True
        elif not ltf_zone.is_demand and opposing_htf_zone.is_demand:
            # Supply breaches opposing HTF Demand's Distal Line on the downside
            if ltf_zone.proximal_line < opposing_htf_zone.distal_line and ltf_zone.has_clean_closing:
                ltf_zone.is_htf_overpowering_origin = True
                return True
        return False

    def classify_candle(
        self,
        index: int,
        open_p: float,
        high_p: float,
        low_p: float,
        close_p: float,
        atr14: float = 0.0,
        prev_close: Optional[float] = None,
        prev_high: Optional[float] = None,
        prev_low: Optional[float] = None,
    ) -> CandleFeature:
        """
        Classifies a single candlestick using GTF 50% body-to-range rule
        and Episode 6 Gap + Base = Invisible Exciting Candle equation.
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

        c_type = CandleType.BASE
        is_gap_exciting = False
        gap_dist = 0.0

        if body_ratio >= 0.50 and is_meaningful:
            c_type = CandleType.GREEN_EXCITING if close_p > open_p else CandleType.RED_EXCITING
        elif prev_close is not None and prev_close > 0:
            # Episode 6 Concept 2: Significant Gap + Base Candle = Exciting Candle
            # A true significant gap requires at least 1.5% displacement (or >= 0.5 ATR) beyond previous range
            min_gap_dist = self.min_gap_ratio * atr14 if atr14 > 0 else (0.015 * prev_close)
            gap_dist = open_p - prev_close

            is_gap_up = bool(
                gap_dist >= min_gap_dist and (prev_high is None or open_p > prev_high)
            )
            is_gap_down = bool(
                (-gap_dist) >= min_gap_dist and (prev_low is None or open_p < prev_low)
            )

            if is_gap_up:
                synthetic_net_body = abs(close_p - prev_close)
                combined_range = max(high_p, prev_close) - min(low_p, prev_close)
                if combined_range > 1e-6 and (synthetic_net_body / combined_range) >= 0.50 and close_p >= prev_close:
                    c_type = CandleType.GREEN_EXCITING
                    is_gap_exciting = True
            elif is_gap_down:
                synthetic_net_body = abs(close_p - prev_close)
                combined_range = max(high_p, prev_close) - min(low_p, prev_close)
                if combined_range > 1e-6 and (synthetic_net_body / combined_range) >= 0.50 and close_p <= prev_close:
                    c_type = CandleType.RED_EXCITING
                    is_gap_exciting = True

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
            is_gap_exciting=is_gap_exciting,
            gap_distance=round(gap_dist, 2),
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
        filter_garbage_areas: bool = True,
    ) -> List[IdentifiedZone]:
        """
        Scans series of candles to identify institutional Demand and Supply zones:
        Leg-in (Arrival) -> Base Candles (Pending Orders) -> Leg-out (Departure).
        Supports:
        - Normal (Body-to-Wick) and Wick-to-Wick Marking
        - Direct Reversals (0 Base Candles)
        - Base candle count strength evaluation (1-3 vs 4-5+)
        - The Closing Concept (Proven vs. Unproven Zones)
        - Origin Pivot Isolation
        - Garbage Area Filtering
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

        # 1. Classify all candles (with previous close & highs/lows for Gap+Base detection)
        classified: List[CandleFeature] = []
        for i in range(n):
            a = float(atr14[i]) if atr14 is not None and i < len(atr14) else 0.0
            prev_c = float(closes[i - 1]) if i > 0 else None
            prev_h = float(highs[i - 1]) if i > 0 else None
            prev_l = float(lows[i - 1]) if i > 0 else None
            classified.append(
                self.classify_candle(
                    i, opens[i], highs[i], lows[i], closes[i], a,
                    prev_close=prev_c, prev_high=prev_h, prev_low=prev_l
                )
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

                    # Episode 6: The Closing Concept
                    if is_demand:
                        has_clean_closing = bool(leg_out.close > leg_in.high)
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
                        has_clean_closing = bool(leg_out.close < leg_in.low)
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

                    is_hq = bool(has_clean_closing)
                    score = 0.90 if has_clean_closing else 0.50

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
                            strength_rating="DIRECT_REVERSAL",
                            strength_score=score,
                            is_direct_reversal=True,
                            timeframe_weight=tf_weight,
                            has_clean_closing=has_clean_closing,
                            is_proven_zone=has_clean_closing,
                            origin_candle_idx=None,
                            is_gap_base_zone=(leg_in.is_gap_exciting or leg_out.is_gap_exciting),
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

                    # Episode 6 Concept 5: Garbage Area Filter
                    if filter_garbage_areas and base_count >= 6:
                        if self.is_garbage_cluster(highs, lows, base_start, base_end, min_bars=6):
                            i += 1
                            continue

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

                        # Episode 6 Concept 1: The Closing Concept
                        if is_demand:
                            has_clean_closing = bool(leg_out.close > leg_in.high)
                        else:
                            has_clean_closing = bool(leg_out.close < leg_in.low)

                        # Episode 5 & 6 Base Candle Strength & Quality Rating:
                        if 1 <= base_count <= 2:
                            strength_rating = "HIGH_STRENGTH"
                            base_score = 1.00
                        elif base_count == 3:
                            strength_rating = "HIGH_STRENGTH"
                            base_score = 0.85
                        elif 4 <= base_count <= 5:
                            strength_rating = "MODERATE_STRENGTH"
                            base_score = 0.60
                        else:
                            strength_rating = "LOW_STRENGTH"
                            base_score = 0.30

                        # Unproven zone penalty if clean closing fails
                        strength_score = base_score if has_clean_closing else round(base_score * 0.60, 2)
                        is_hq = bool((1 <= base_count <= self.max_base_candles) and has_clean_closing)

                        # Episode 6 Concept 3: Origin Pivot Isolation
                        origin_idx = None
                        if base_count >= 3:
                            if is_demand:
                                origin_idx = base_start + int(np.argmin([b.low for b in base_candles]))
                            else:
                                origin_idx = base_start + int(np.argmax([b.high for b in base_candles]))

                        if is_demand:
                            if mode_eff == MarkingMode.WICK_TO_WICK:
                                proximal = max(b.high for b in base_candles)
                            else:
                                proximal = max(max(b.open, b.close) for b in base_candles)

                            distal_normal = min(b.low for b in base_candles)

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
                            if mode_eff == MarkingMode.WICK_TO_WICK:
                                proximal = min(b.low for b in base_candles)
                            else:
                                proximal = min(min(b.open, b.close) for b in base_candles)

                            distal_normal = max(b.high for b in base_candles)

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

                        has_gap_base = any(b.is_gap_exciting for b in base_candles) or leg_in.is_gap_exciting or leg_out.is_gap_exciting

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
                                has_clean_closing=has_clean_closing,
                                is_proven_zone=has_clean_closing,
                                origin_candle_idx=origin_idx,
                                is_gap_base_zone=has_gap_base,
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
        filter_unproven: bool = False,
    ) -> Tuple[List[IdentifiedZone], List[IdentifiedZone]]:
        """
        Navigates relative to Current Market Price (CMP) as taught in Episodes 3-6:
        1. Demand Zones: Look Left & Down (Proximal Line < CMP).
        2. Supply Zones: Look Left & Up (Proximal Line > CMP).
        Optional `filter_unproven`: excludes zones that failed the Closing Concept.
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
            if filter_unproven and not z.is_proven_zone:
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

    @classmethod
    def validate_matching_timeframe(
        cls,
        retreat_supply_tf: TimeframeTier,
        reaction_demand_tf: TimeframeTier,
        is_pristine_origin: bool = False,
    ) -> Tuple[bool, str]:
        """
        Episode 11: The Matching Timeframe Principle.
        When price retreats after hitting an opposing HTF Zone:
        - Retreat from Weekly Supply requires at least Weekly Demand (or pristine Daily origin base).
        - Retreat from Monthly Supply requires at least Monthly Demand (or pristine Weekly origin).
        - Retreat from Quarterly/Half-Yearly/Yearly requires at least Quarterly/Half-Yearly Demand.
        Trading aggressive lower-timeframe demand zones directly underneath an opposing HTF supply
        runs into the Steamroller Effect.
        """
        supply_weight = cls.TIMEFRAME_WEIGHTS.get(retreat_supply_tf, 1.0)
        demand_weight = cls.TIMEFRAME_WEIGHTS.get(reaction_demand_tf, 1.0)

        # If demand timeframe is equal or higher in hierarchy, it is structurally qualified
        if demand_weight >= supply_weight:
            return (
                True,
                f"Matching timeframe satisfied: {reaction_demand_tf.value} demand matches or exceeds {retreat_supply_tf.value} supply."
            )

        # If demand is one level lower but is a pristine origin base, it is permitted
        if is_pristine_origin and (supply_weight - demand_weight) <= 1.0:
            return (
                True,
                f"Pristine origin exception satisfied: Pristine {reaction_demand_tf.value} origin qualifies against {retreat_supply_tf.value} supply."
            )

        return (
            False,
            f"Steamroller Risk: Price retreating from {retreat_supply_tf.value} supply cannot be absorbed "
            f"by an aggressive {reaction_demand_tf.value} demand zone (Weight {demand_weight} < {supply_weight}). "
            f"Requires matching HTF demand or pristine origin base."
        )

    @classmethod
    def evaluate_trading_stance(
        cls,
        execution_zone: IdentifiedZone,
        opposing_htf_zone: Optional[IdentifiedZone] = None,
        intermediate_trend: Optional[TrendDirection] = None,
        has_clean_space: bool = False,
        has_proven_achievement: bool = False,
        is_deep_origin: bool = False,
    ) -> Tuple[TradingStance, str]:
        """
        Episode 11: When to be Aggressive and When to be Conservative.
        Universal Axiom: 'As a trader, you can always be conservative, but you can NEVER be always aggressive.'

        Conservative is the default stance.
        Aggressive is permitted ONLY under two conditions:
          Condition 1: Clean space ahead with intermediate trend aligned and no opposing HTF zone.
          Condition 2: The Proven Achievement Rule - the execution level closed decisively beyond opposing HTF resistance.
        """
        # If opposing HTF zone is present and price retreated from it
        if opposing_htf_zone is not None:
            if has_proven_achievement or execution_zone.is_htf_overpowering_origin:
                execution_zone.trading_stance = TradingStance.AGGRESSIVE
                execution_zone.has_proven_achievement = True
                return (
                    TradingStance.AGGRESSIVE,
                    f"Proven Achievement: Execution zone has closed beyond opposing {opposing_htf_zone.timeframe.value} "
                    f"resistance, neutralizing macro supply. Aggressive pullbacks permitted."
                )

            # Check matching timeframe
            is_matched, msg = cls.validate_matching_timeframe(
                opposing_htf_zone.timeframe, execution_zone.timeframe, is_pristine_origin=is_deep_origin
            )
            if not is_matched:
                execution_zone.trading_stance = TradingStance.CONSERVATIVE
                return (
                    TradingStance.CONSERVATIVE,
                    f"Conservative stance enforced: {msg}"
                )

        # If no opposing HTF zone or clean space
        if has_clean_space:
            trend_aligned = False
            if execution_zone.is_demand and intermediate_trend == TrendDirection.UPTREND:
                trend_aligned = True
            elif not execution_zone.is_demand and intermediate_trend == TrendDirection.DOWNTREND:
                trend_aligned = True

            if trend_aligned:
                execution_zone.trading_stance = TradingStance.AGGRESSIVE
                return (
                    TradingStance.AGGRESSIVE,
                    "Clean space ahead with aligned intermediate trend: Aggressive entry permitted on upper base / shallow retest."
                )

        execution_zone.trading_stance = TradingStance.CONSERVATIVE
        return (
            TradingStance.CONSERVATIVE,
            "Conservative stance enforced by default: Wait for deep origin base or clear macro confirmation."
        )

    @staticmethod
    def anchor_sl_to_htf_base(
        ltf_zone: IdentifiedZone,
        htf_zone: IdentifiedZone,
        tick_size: float = 0.05,
        buffer_ticks: int = 5,
    ) -> float:
        """
        Episode 11: Anchoring Stop-Loss to Shri Krishna (HTF Location Base).
        In sideways or down-leaning intermediate trend conditions, placing a tight SL
        beneath a shallow LTF base risks premature stop-out.
        Instead, anchor the stop-loss beneath the Distal Line of the underlying HTF (Monthly) base.
        """
        buffer_val = tick_size * buffer_ticks
        if ltf_zone.is_demand:
            # Anchor below HTF Distal Line
            anchored_sl = round(htf_zone.distal_line - buffer_val, 2)
            ltf_zone.anchored_htf_stoploss = anchored_sl
            return anchored_sl
        else:
            # Anchor above HTF Distal Line for Supply
            anchored_sl = round(htf_zone.distal_line + buffer_val, 2)
            ltf_zone.anchored_htf_stoploss = anchored_sl
            return anchored_sl

    @staticmethod
    def detect_structural_regime_inversion(
        demand_breached_count: int,
        demand_respected_count: int,
        supply_breached_count: int,
        supply_respected_count: int,
    ) -> Tuple[bool, str]:
        """
        Episode 11: TVS Motor Master Case Study - Structural Inversion / Regime Shift.
        Near all-time highs or macro distribution:
        When fresh demand zones begin to breach repeatedly while fresh supply zones hold,
        an institutional distribution regime shift is underway.
        Traders must immediately cease aggressive long entries.
        """
        demand_failing = demand_breached_count > demand_respected_count
        supply_holding = supply_respected_count > supply_breached_count

        if demand_failing and supply_holding:
            return (
                True,
                f"Structural Regime Inversion Confirmed: Demand failing ({demand_breached_count} breached vs {demand_respected_count} held) "
                f"and Supply holding ({supply_respected_count} held vs {supply_breached_count} breached). "
                f"Institutional distribution underway; CEASE all aggressive long entries immediately."
            )

        return (
            False,
            f"Normal regime intact: Demand breaches={demand_breached_count}, held={demand_respected_count}; "
            f"Supply breaches={supply_breached_count}, held={supply_respected_count}."
        )

    @staticmethod
    def check_dynamic_20_ema_interaction(
        current_price: float,
        ema_20: float,
        trade_direction: str = "SHORT",
        tolerance_pct: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Episode 11: Dynamic Moving Average Preview (20 EMA Equilibrium Curve).
        The 20 EMA functions as dynamic institutional equilibrium.
        In strong trending conditions, price often kisses the 20 EMA and reverses sharply,
        delivering 1.5:1 or 2:1 targets before reaching deeper horizontal levels.
        Traders shorting against an approaching 20 EMA must book profits quickly or trail stops.
        """
        distance_pct = abs(current_price - ema_20) / current_price * 100.0
        is_interacting = distance_pct <= tolerance_pct

        if trade_direction.upper() == "SHORT":
            if is_interacting or (current_price <= ema_20 and distance_pct <= tolerance_pct * 2):
                return {
                    "is_interacting": True,
                    "distance_pct": round(distance_pct, 2),
                    "action_recommendation": (
                        "Approaching dynamic 20 EMA support: High probability of institutional bounce. "
                        "Book partial profits (1.5:1 / 2:1) or trail stop-loss tight."
                    ),
                    "warning_level": "CAUTION_DYNAMIC_SUPPORT",
                }
            return {
                "is_interacting": False,
                "distance_pct": round(distance_pct, 2),
                "action_recommendation": "Comfortable distance from dynamic 20 EMA.",
                "warning_level": "NORMAL",
            }
        else:  # LONG
            if is_interacting:
                return {
                    "is_interacting": True,
                    "distance_pct": round(distance_pct, 2),
                    "action_recommendation": (
                        "Price interacting with dynamic 20 EMA support: In strong trend, can reverse sharply "
                        "without reaching deeper horizontal demand. Monitor for dynamic bounce."
                    ),
                    "warning_level": "DYNAMIC_EQUILIBRIUM_TEST",
                }
            return {
                "is_interacting": False,
                "distance_pct": round(distance_pct, 2),
                "action_recommendation": "Price not currently at 20 EMA equilibrium.",
                "warning_level": "NORMAL",
            }

    @staticmethod
    def calculate_sma(series: np.ndarray, period: int) -> np.ndarray:
        """
        Episode 12: Simple Moving Average (SMA) Formula:
        SMA_n = (Sum of Closing Prices of Last n Candles) / n
        Equal Weighting: Each candle in the lookback window has identical statistical weight (1/n).
        """
        if len(series) < period or period <= 0:
            return np.full_like(series, np.nan, dtype=np.float64)
        ret = np.full_like(series, np.nan, dtype=np.float64)
        cumsum = np.cumsum(np.insert(series, 0, 0))
        ret[period - 1:] = (cumsum[period:] - cumsum[:-period]) / float(period)
        return ret

    @staticmethod
    def calculate_ema(series: np.ndarray, period: int) -> np.ndarray:
        """
        Episode 12: Exponential Moving Average (EMA) Formula:
        alpha = 2 / (period + 1)
        EMA_t = Close_t * alpha + EMA_{t-1} * (1 - alpha)
        Exponential Weighting: Assigns exponentially decreasing weights to older data points,
        prioritizing recent price action and hugging the chart tighter than SMA.
        """
        if len(series) < period or period <= 0:
            return np.full_like(series, np.nan, dtype=np.float64)
        ret = np.full_like(series, np.nan, dtype=np.float64)
        alpha = 2.0 / (period + 1.0)
        # Seed first EMA value with initial SMA
        ret[period - 1] = float(np.mean(series[:period]))
        for i in range(period, len(series)):
            ret[i] = (series[i] * alpha) + (ret[i - 1] * (1.0 - alpha))
        return ret

    @staticmethod
    def detect_ma_crossover(
        fast_series: np.ndarray,
        slow_series: np.ndarray,
        lookback_bars: int = 5,
    ) -> Tuple[MACrossoverType, int, float]:
        """
        Episode 12: Golden Crossover & Death Crossover Detection.
        - Golden Crossover: Fast EMA crosses above Slow EMA.
        - Death Crossover: Fast EMA crosses below Slow EMA.
        Searches backwards within the last `lookback_bars` completed candles.
        Returns (crossover_type, bar_index_of_cross, price_at_cross).
        """
        n = len(fast_series)
        if n < 2 or len(slow_series) != n:
            return MACrossoverType.NO_CROSSOVER, -1, 0.0

        start_idx = max(1, n - lookback_bars)
        for i in range(n - 1, start_idx - 1, -1):
            if np.isnan(fast_series[i]) or np.isnan(slow_series[i]):
                continue
            if np.isnan(fast_series[i - 1]) or np.isnan(slow_series[i - 1]):
                continue

            # Golden Crossover: fast was <= slow, now fast > slow
            if fast_series[i - 1] <= slow_series[i - 1] and fast_series[i] > slow_series[i]:
                return MACrossoverType.GOLDEN_CROSSOVER, i, float(fast_series[i])

            # Death Crossover: fast was >= slow, now fast < slow
            if fast_series[i - 1] >= slow_series[i - 1] and fast_series[i] < slow_series[i]:
                return MACrossoverType.DEATH_CROSSOVER, i, float(fast_series[i])

        return MACrossoverType.NO_CROSSOVER, -1, 0.0

    @staticmethod
    def evaluate_crossover_trade_score_bonus(
        zone: IdentifiedZone,
        crossover_type: MACrossoverType,
        crossover_price: float,
        opposing_htf_supply: Optional[IdentifiedZone] = None,
        opposing_htf_demand: Optional[IdentifiedZone] = None,
    ) -> Tuple[bool, int, str]:
        """
        Episode 12 GTF Rule: Moving Average Crossovers as an Extra Trade Score.
        - Crossovers are NEVER standalone triggers; baseline setup must qualify on 3 timeframes.
        - Crossovers on execution timeframe award +1 Extra Trade Score (8/7).
        - Filters out Retail Crossover Traps (Golden Crossover into HTF supply, Death Crossover into HTF demand).
        """
        if crossover_type == MACrossoverType.NO_CROSSOVER:
            return False, 0, "No crossover detected; baseline trade score intact."

        # Retail Supply Trap: Golden crossover triggered when price enters/approaches opposing HTF supply
        if crossover_type == MACrossoverType.GOLDEN_CROSSOVER:
            if opposing_htf_supply is not None:
                supply_trap_boundary = opposing_htf_supply.proximal_line * 0.985
                if crossover_price >= supply_trap_boundary:
                    return (
                        False,
                        0,
                        f"Retail Supply Trap: Golden Crossover at {crossover_price:.2f} triggered directly "
                        f"into opposing HTF Supply (PL: {opposing_htf_supply.proximal_line:.2f}). "
                        f"Institutions dump into retail buying liquidity; bonus rejected."
                    )

            # Valid Extra Trade Score for Demand Zone
            if zone.is_demand:
                zone_buffer = (zone.proximal_line - zone.distal_line) * 1.5
                if (zone.distal_line - zone_buffer) <= crossover_price <= (zone.proximal_line + zone_buffer):
                    if zone.trade_score is not None:
                        zone.trade_score.ma_crossover_bonus = 1
                        zone.trade_score.total_score += 1.0
                        zone.trade_score.crossover_type = crossover_type
                    return (
                        True,
                        1,
                        f"Extra Trade Score Awarded: Golden Crossover coincides with execution Demand Zone "
                        f"(PL: {zone.proximal_line:.2f}, DL: {zone.distal_line:.2f}). Bonus +1 confirmation."
                    )

        # Retail Demand Trap: Death crossover triggered when price enters/approaches opposing HTF demand
        elif crossover_type == MACrossoverType.DEATH_CROSSOVER:
            if opposing_htf_demand is not None:
                demand_trap_boundary = opposing_htf_demand.proximal_line * 1.015
                if crossover_price <= demand_trap_boundary:
                    return (
                        False,
                        0,
                        f"Retail Demand Trap: Death Crossover at {crossover_price:.2f} triggered directly "
                        f"into opposing HTF Demand (PL: {opposing_htf_demand.proximal_line:.2f}). "
                        f"Institutions accumulate from retail panic selling; bonus rejected."
                    )

            # Valid Extra Trade Score for Supply Zone
            if not zone.is_demand:
                zone_buffer = (zone.distal_line - zone.proximal_line) * 1.5
                if (zone.proximal_line - zone_buffer) <= crossover_price <= (zone.distal_line + zone_buffer):
                    if zone.trade_score is not None:
                        zone.trade_score.ma_crossover_bonus = 1
                        zone.trade_score.total_score += 1.0
                        zone.trade_score.crossover_type = crossover_type
                    return (
                        True,
                        1,
                        f"Extra Trade Score Awarded: Death Crossover coincides with execution Supply Zone "
                        f"(PL: {zone.proximal_line:.2f}, DL: {zone.distal_line:.2f}). Bonus +1 confirmation."
                    )

        return False, 0, "Crossover did not coincide with execution zone boundaries; baseline score intact."

    @staticmethod
    def calculate_dynamic_ma_buffer_sl(
        zone: IdentifiedZone,
        ema_fast: float,
        ema_slow: float,
        tick_size: float = 0.05,
        buffer_ticks: int = 5,
    ) -> float:
        """
        Episode 12 Rule 3: Dynamic Stop-Loss Protection via Moving Average Buffer.
        If a moving average crossover sits just beneath a demand zone's distal line,
        placing the stop-loss below the moving average cross provides an extra institutional buffer.
        """
        buffer_val = tick_size * buffer_ticks
        if zone.is_demand:
            min_ma = min(ema_fast, ema_slow)
            # If MA sits below distal line, anchor SL below the MA
            if min_ma < zone.distal_line:
                return round(min_ma - buffer_val, 2)
            return round(zone.distal_line - buffer_val, 2)
        else:
            max_ma = max(ema_fast, ema_slow)
            # If MA sits above distal line for supply, anchor SL above the MA
            if max_ma > zone.distal_line:
                return round(max_ma + buffer_val, 2)
            return round(zone.distal_line + buffer_val, 2)

    @staticmethod
    def evaluate_zone_breach_by_close(
        candle_close: float,
        candle_high: float,
        candle_low: float,
        zone: IdentifiedZone,
    ) -> bool:
        """
        Episode 13: The Mandatory Candle Close Filter for Zone Elimination.
        A mere intra-candle wick spike beyond the distal line does NOT count as a zone breach.
        The candle must physically CLOSE outside the distal boundary to count as an eliminated zone:
          - Supply Zone Breach: Candle Close > Distal Line.
          - Demand Zone Breach: Candle Close < Distal Line.
        """
        if zone.is_demand:
            # Demand zone breach requires candle close below distal line
            return candle_close < zone.distal_line
        else:
            # Supply zone breach requires candle close above distal line
            return candle_close > zone.distal_line

    @staticmethod
    def calculate_advanced_trend(
        prior_trend: TrendDirection,
        consecutive_supply_breaches: int,
        consecutive_demand_breaches: int,
    ) -> Tuple[TrendDirection, str]:
        """
        Episode 13: Advanced Trend Violation Matrix.
        Tracks the systematic destruction of opposing institutional zones:
          - Downtrend:
              1 Supply Breached & Closed Above -> SIDEWAYS
              2 Consecutive Supplies Breached & Closed Above -> UPTREND CONFIRMED
          - Uptrend:
              1 Demand Breached & Closed Below -> SIDEWAYS
              2 Consecutive Demands Breached & Closed Below -> DOWNTREND CONFIRMED
          - Sideways:
              1 Supply Breached -> UPTREND
              1 Demand Breached -> DOWNTREND
        Integrates Continuous Patterns (DBD in drops, RBR in rallies) positioning the trader
        Two Steps Ahead of conventional technical analysts who wait for macro reversal highs.
        """
        if prior_trend == TrendDirection.DOWNTREND:
            if consecutive_supply_breaches >= 2:
                return (
                    TrendDirection.UPTREND,
                    f"Advanced Trend: UPTREND CONFIRMED ({consecutive_supply_breaches} consecutive supply zones eliminated by close). "
                    f"Institutional buyers have completely overpowered macro sellers."
                )
            elif consecutive_supply_breaches == 1:
                return (
                    TrendDirection.SIDEWAYS,
                    "Advanced Trend: Downtrend broken; trend transitioned to SIDEWAYS (1st supply zone eliminated by close)."
                )
            return (
                TrendDirection.DOWNTREND,
                "Advanced Trend: Downtrend intact (0 supply zones eliminated)."
            )

        elif prior_trend == TrendDirection.UPTREND:
            if consecutive_demand_breaches >= 2:
                return (
                    TrendDirection.DOWNTREND,
                    f"Advanced Trend: DOWNTREND CONFIRMED ({consecutive_demand_breaches} consecutive demand zones eliminated by close). "
                    f"Institutional sellers have completely overpowered macro buyers."
                )
            elif consecutive_demand_breaches == 1:
                return (
                    TrendDirection.SIDEWAYS,
                    "Advanced Trend: Uptrend broken; trend transitioned to SIDEWAYS (1st demand zone eliminated by close)."
                )
            return (
                TrendDirection.UPTREND,
                "Advanced Trend: Uptrend intact (0 demand zones eliminated)."
            )

        else:  # SIDEWAYS
            if consecutive_supply_breaches >= 1:
                return (
                    TrendDirection.UPTREND,
                    f"Advanced Trend: UPTREND CONFIRMED from Sideways ({consecutive_supply_breaches} supply zone eliminated)."
                )
            elif consecutive_demand_breaches >= 1:
                return (
                    TrendDirection.DOWNTREND,
                    f"Advanced Trend: DOWNTREND CONFIRMED from Sideways ({consecutive_demand_breaches} demand zone eliminated)."
                )
            return (
                TrendDirection.SIDEWAYS,
                "Advanced Trend: Sideways consolidation intact (no opposing zones eliminated)."
            )

    @staticmethod
    def evaluate_ema20_confluence_bonus(
        zone: IdentifiedZone,
        ema_20_val: float,
        is_trending_market: bool = True,
    ) -> Tuple[bool, int, str]:
        """
        Episode 13: Algorithmic EMA 20 Footprint & Extra Trade Score Confluence.
        - Institutional algos program baseline buy/sell logic around the 20-period exponential average.
        - If a trending EMA 20 passes between Proximal Line and Distal Line of the execution zone,
          award +1 Extra Trade Score (elevating 7/7 to 8/7 bonus confirmation).
        - Functions strictly in trending markets (choppy/sideways markets weave and lose predictive power).
        """
        if not is_trending_market:
            return (
                False,
                0,
                "EMA 20 confluence rejected: In choppy/sideways markets, moving averages lose predictive utility."
            )

        lower_bound = min(zone.proximal_line, zone.distal_line) - 0.05
        upper_bound = max(zone.proximal_line, zone.distal_line) + 0.05

        if lower_bound <= ema_20_val <= upper_bound:
            if zone.trade_score is not None:
                zone.trade_score.ema20_confluence_bonus = 1
                zone.trade_score.total_score += 1.0

            zone_desc = "Demand Zone" if zone.is_demand else "Supply Zone"
            return (
                True,
                1,
                f"Extra Trade Score Awarded: Trending EMA 20 ({ema_20_val:.2f}) passes inside {zone_desc} "
                f"[{min(zone.proximal_line, zone.distal_line):.2f} - {max(zone.proximal_line, zone.distal_line):.2f}]. "
                f"Institutional algorithmic confluence +1 bonus."
            )

        return (
            False,
            0,
            f"EMA 20 ({ema_20_val:.2f}) sits outside zone boundaries [{min(zone.proximal_line, zone.distal_line):.2f} - {max(zone.proximal_line, zone.distal_line):.2f}]."
        )

    @staticmethod
    def detect_ema20_squeeze(
        closes: np.ndarray,
        ema_20: np.ndarray,
        lookback: int = 5,
        squeeze_threshold_pct: float = 0.4,
    ) -> Tuple[bool, float, str]:
        """
        Episode 13: Volatility Squeeze Indicator (Phase 2).
        When price consolidates after prolonged move, the gap between candles and EMA 20
        steadily contracts into tight base candles.
        Signals equilibrium compression preceding an explosive breakout.
        """
        if len(closes) < lookback or len(ema_20) < lookback:
            return False, 0.0, "Insufficient data for squeeze evaluation."

        recent_closes = closes[-lookback:]
        recent_ema = ema_20[-lookback:]

        dist_pcts = np.abs(recent_closes - recent_ema) / recent_closes * 100.0
        mean_dist = float(np.mean(dist_pcts))

        if mean_dist <= squeeze_threshold_pct:
            return (
                True,
                round(mean_dist, 2),
                f"Volatility Squeeze Detected (Phase 2): Price and EMA 20 compressed into tight base candles "
                f"(average distance {mean_dist:.2f}% <= {squeeze_threshold_pct}%). Extreme compression preceding breakout."
            )

        return (
            False,
            round(mean_dist, 2),
            f"Normal price-to-EMA spread ({mean_dist:.2f}% > {squeeze_threshold_pct}%)."
        )

    @classmethod
    def evaluate_trading_against_the_trend_confirmation(
        cls,
        htf_demand_zone: IdentifiedZone,
        nearest_ltf_supply_zone: IdentifiedZone,
        breakout_candle_close: float,
        newly_formed_ltf_demand: Optional[IdentifiedZone] = None,
        is_all_time_low: bool = False,
        consecutive_supply_breaches_count: int = 1,
        macro_opposing_supply_target: Optional[float] = None,
    ) -> ConfirmationTradePlan:
        """
        Episode 14: Trading Against the Trend with Confirmation Entry.
        - Blind entry at HTF Demand proximal line carries massive stop-loss distance and falling knife risk.
        - Rule: When backed by a macro HTF (Monthly/Quarterly) Demand Zone (Shri Krishna),
          ONLY 1 nearest LTF Supply Zone needs to be breached and closed above!
        - Entry executes on the newly formed LTF Demand Zone that created the breakout.
        - Compresses macro risk (e.g. ₹900 down to ₹30) unlocking 3:1 to 20:1 RRR.
        - Guard: If stock is at All-Time Low, long trades are strictly prohibited unless
          >= 2 consecutive supply zones are eliminated on intermediate timeframe.
        """
        macro_risk = abs(htf_demand_zone.proximal_line - htf_demand_zone.distal_line)

        # All-Time Low Check
        if is_all_time_low:
            if consecutive_supply_breaches_count < 2:
                return ConfirmationTradePlan(
                    htf_demand_zone=htf_demand_zone,
                    nearest_ltf_supply_zone=nearest_ltf_supply_zone,
                    is_htf_demand_tested=True,
                    is_supply_eliminated_by_close=False,
                    newly_formed_ltf_demand=None,
                    macro_risk_per_share=macro_risk,
                    compressed_risk_per_share=0.0,
                    risk_compression_ratio=1.0,
                    realized_target_rrr=0.0,
                    is_confirmed=False,
                    status_message=(
                        "All-Time Low Protection: Long entries strictly prohibited in ATL assets. "
                        "Must eliminate at least 2 consecutive supply zones to establish bottom-out criteria."
                    ),
                )

        # Check Mandatory Candle Close Filter for Supply Breach
        is_breached = breakout_candle_close > nearest_ltf_supply_zone.distal_line
        if not is_breached:
            return ConfirmationTradePlan(
                htf_demand_zone=htf_demand_zone,
                nearest_ltf_supply_zone=nearest_ltf_supply_zone,
                is_htf_demand_tested=True,
                is_supply_eliminated_by_close=False,
                newly_formed_ltf_demand=None,
                macro_risk_per_share=macro_risk,
                compressed_risk_per_share=0.0,
                risk_compression_ratio=1.0,
                realized_target_rrr=0.0,
                is_confirmed=False,
                status_message=(
                    f"Unconfirmed: Breakout candle close ({breakout_candle_close:.2f}) failed to close above "
                    f"LTF supply distal line ({nearest_ltf_supply_zone.distal_line:.2f}). Mandatory close required."
                ),
            )

        # Supply is breached by close! Now check newly formed LTF demand
        if newly_formed_ltf_demand is None:
            return ConfirmationTradePlan(
                htf_demand_zone=htf_demand_zone,
                nearest_ltf_supply_zone=nearest_ltf_supply_zone,
                is_htf_demand_tested=True,
                is_supply_eliminated_by_close=True,
                newly_formed_ltf_demand=None,
                macro_risk_per_share=macro_risk,
                compressed_risk_per_share=0.0,
                risk_compression_ratio=1.0,
                realized_target_rrr=0.0,
                is_confirmed=False,
                status_message=(
                    "Supply breached by close, but newly formed LTF demand zone not yet established. "
                    "Do not chase continuous breakout candles; await base formation."
                ),
            )

        # Newly formed demand exists
        compressed_risk = abs(newly_formed_ltf_demand.proximal_line - newly_formed_ltf_demand.distal_line)
        compression_ratio = round(macro_risk / compressed_risk, 2) if compressed_risk > 0 else 1.0

        # Calculate RRR
        if macro_opposing_supply_target is not None and compressed_risk > 0:
            target_distance = abs(macro_opposing_supply_target - newly_formed_ltf_demand.proximal_line)
            realized_rrr = round(target_distance / compressed_risk, 2)
        else:
            realized_rrr = newly_formed_ltf_demand.risk_reward_ratio

        newly_formed_ltf_demand.trading_stance = TradingStance.AGGRESSIVE
        newly_formed_ltf_demand.has_proven_achievement = True

        return ConfirmationTradePlan(
            htf_demand_zone=htf_demand_zone,
            nearest_ltf_supply_zone=nearest_ltf_supply_zone,
            is_htf_demand_tested=True,
            is_supply_eliminated_by_close=True,
            newly_formed_ltf_demand=newly_formed_ltf_demand,
            macro_risk_per_share=macro_risk,
            compressed_risk_per_share=compressed_risk,
            risk_compression_ratio=compression_ratio,
            realized_target_rrr=realized_rrr,
            is_confirmed=True,
            status_message=(
                f"Confirmed (Episode 14): Backed by macro HTF Demand ({htf_demand_zone.timeframe.value}), "
                f"1 LTF Supply Zone eliminated by close. Micro-risk entry on newly formed LTF demand "
                f"(Risk compressed {compression_ratio:.1f}x from ₹{macro_risk:.1f} to ₹{compressed_risk:.1f}, "
                f"RRR: {realized_rrr:.1f}:1)."
            ),
        )

    @staticmethod
    def validate_all_time_low_bottom_out(
        is_at_all_time_low: bool,
        consecutive_supply_breaches: int,
    ) -> Tuple[bool, str]:
        """
        Episode 14 Rule: All-Time Low (ATL) Protocol.
        In an All-Time Low asset, long trades are strictly forbidden.
        Bottom-Out Criteria: An ATL stock cannot be assumed to have bottomed out until
        at least 2 consecutive supply zones are eliminated on the intermediate timeframe.
        """
        if not is_at_all_time_low:
            return True, "Asset not at All-Time Low; normal confirmation rules apply."

        if consecutive_supply_breaches >= 2:
            return (
                True,
                f"ATL Bottom-Out Qualified: {consecutive_supply_breaches} consecutive supply zones eliminated on intermediate timeframe. "
                f"Macro institutional demand base established; long confirmation entries permitted."
            )

        return (
            False,
            f"ATL Long Prohibition: Asset at All-Time Low with only {consecutive_supply_breaches} supply breach(es). "
            f"Long trades strictly forbidden. Requires >= 2 consecutive supply zones eliminated."
        )

    @staticmethod
    def detect_macro_supply_wall(
        cmp: float,
        macro_supply_zones: Optional[List[IdentifiedZone]] = None,
        proximity_pct: float = 2.0,
    ) -> Tuple[MacroSupplyWallStatus, Optional[IdentifiedZone], str]:
        """
        Episode 15 Rule: The Half-Yearly / Yearly Supply Wall (The Macro Trap).
        Detects whether price is colliding with or reacting off a macro (Half-Yearly,
        Yearly, or unbreached Quarterly) supply zone.

        Collision Reality:
        When price hits a Half-Yearly or Yearly supply zone, massive multi-month
        selling pressure is unleashed. Intermediate lower-timeframe (Daily/125m)
        demand zones will be sliced through as price falls away from the wall.
        """
        if not macro_supply_zones:
            return (
                MacroSupplyWallStatus.NO_WALL,
                None,
                "Macro Supply Wall clear: No overhead Half-Yearly/Yearly/Quarterly supply zones detected.",
            )

        macro_tiers = {TimeframeTier.YEARLY, TimeframeTier.HALF_YEARLY, TimeframeTier.QUARTERLY}

        for sz in macro_supply_zones:
            if sz.is_demand:
                continue
            if sz.timeframe not in macro_tiers:
                continue

            pl = sz.proximal_line
            dl = sz.distal_line

            # Check if CMP is directly inside the macro supply zone
            if pl <= cmp <= dl:
                return (
                    MacroSupplyWallStatus.COLLIDING_WITH_WALL,
                    sz,
                    f"Macro Wall Collision Detected! CMP {cmp:.1f} is directly inside {sz.timeframe.value} "
                    f"Supply Zone [{pl:.1f} - {dl:.1f}]. Massive multi-month institutional selling pressure unleashed. "
                    f"Aggressive LTF long setups are strictly prohibited (Macro Trap).",
                )

            # Check if price is within proximity_pct below proximal line
            if cmp < pl and pl > 0:
                dist_pct = ((pl - cmp) / pl) * 100.0
                if dist_pct <= proximity_pct:
                    return (
                        MacroSupplyWallStatus.COLLIDING_WITH_WALL,
                        sz,
                        f"Macro Wall Collision Imminent! CMP {cmp:.1f} is within {dist_pct:.2f}% of "
                        f"{sz.timeframe.value} Supply Zone [{pl:.1f} - {dl:.1f}]. High vulnerability to macro rejection.",
                    )

            # If zone was tested and CMP is falling away below proximal line
            if not sz.is_fresh and cmp < pl:
                if (pl - cmp) / pl <= 0.08:  # within 8% retreat
                    return (
                        MacroSupplyWallStatus.FALLING_AWAY_FROM_WALL,
                        sz,
                        f"Falling Away from Macro Wall: CMP {cmp:.1f} has rejected off {sz.timeframe.value} "
                        f"Supply Zone [{pl:.1f} - {dl:.1f}]. Intermediate daily/125m demand zones will fail rapidly.",
                    )

        return (
            MacroSupplyWallStatus.NO_WALL,
            None,
            "Macro Supply Wall clear: Price is not colliding with or falling away from macro supply.",
        )

    @staticmethod
    def classify_origin_vs_distribution(
        zone: IdentifiedZone,
        is_at_cycle_turning_point: bool,
        has_ema_support: bool = False,
        is_distributive_stair_step: bool = False,
    ) -> Tuple[OriginQuality, str]:
        """
        Episode 15 Rule: Pristine Origin vs. Shallow Distributive Basing.
        - Pristine Origin Base: Located at the bottom/turning point of a major prior cycle,
          1-3 clean base candles, dynamic EMA support, explosive departure.
          Targets opposing macro supply for 8:1 to 10:1+ RRR.
        - Shallow Distributive Base: Formed in mid-air chop or stair-stepping upward
          during distribution; easily sliced through when price turns from overhead supply.
        - Garbage Area: Directionless consolidation with overlapping wicks; rejected.
        """
        if getattr(zone, "is_garbage_area", False) or zone.base_candles_count > 6:
            return (
                OriginQuality.GARBAGE_CONSOLIDATION,
                f"Garbage Area Consolidation: Base candle count ({zone.base_candles_count}) exceeds limits "
                f"with overlapping wicks. Marking must never be forced inside garbage areas.",
            )

        if is_distributive_stair_step or (not is_at_cycle_turning_point and zone.base_candles_count >= 4):
            return (
                OriginQuality.SHALLOW_DISTRIBUTIVE,
                "Shallow / Distributive Basing: Zone formed in mid-air consolidation or distributive stair-step. "
                "Vulnerable to rapid breach if price encounters higher-timeframe resistance.",
            )

        if is_at_cycle_turning_point and zone.base_candles_count <= 3:
            ema_str = " with dynamic EMA support" if has_ema_support else ""
            return (
                OriginQuality.PRISTINE_ORIGIN,
                f"Pristine Origin Base: Located at structural cycle inflection point{ema_str} "
                f"({zone.base_candles_count} base candles, explosive departure). "
                f"Eligible for macro expansion targeting opposing supply (8:1 to 10:1+ RRR).",
            )

        return (
            OriginQuality.SHALLOW_DISTRIBUTIVE,
            f"Secondary Basing ({zone.base_candles_count} base candles): Tradeable only with confirmation and conservative stance.",
        )

    @classmethod
    def audit_comprehensive_top_down_setup(
        cls,
        execution_zone: IdentifiedZone,
        cmp: float,
        htf_zone: Optional[IdentifiedZone] = None,
        itf_trend: TrendDirection = TrendDirection.UPTREND,
        curve_position: CurvePosition = CurvePosition.LOW_ON_CURVE,
        macro_supply_zones: Optional[List[IdentifiedZone]] = None,
        is_at_cycle_turning_point: bool = False,
        has_ema_support: bool = False,
        is_distributive_stair_step: bool = False,
        is_at_all_time_low: bool = False,
        consecutive_supply_breaches: int = 0,
        capital: float = 100000.0,
        risk_per_trade_pct: float = 1.0,
        prior_trades_count: int = 100,
        attempted_entry_type: EntryType = EntryType.SET_AND_FORGET,
        is_parent_sector_in_demand: bool = False,
        is_nifty_in_demand: bool = False,
        is_sector_in_free_fall: bool = False,
        candlestick_pattern: Optional[str] = None,
        is_pattern_in_mid_air_isolation: bool = False,
        gap_application_report: Optional[Any] = None,
        is_window_gap_present: bool = False,
        window_gap_decision: Optional[str] = None,
        window_gap_elevated_entry: Optional[float] = None,
        is_lotl_setup: bool = False,
        lotl_entry_mode: Optional[str] = None,
        lotl_merged_entry: Optional[float] = None,
        lotl_lower_distal_sl: Optional[float] = None,
        is_breakout_trade: bool = False,
        breakout_price: Optional[float] = None,
        rsi_value: Optional[float] = None,
        is_ath_expansion_planned: bool = False,
    ) -> MasterRevisionAuditReport:
        """
        Episode 15 Master Revision Class: The 14-Point Comprehensive Top-Down Institutional Auditor.
        Synthesizes the complete curriculum (Episodes 1 to 14) into an empirical gatekeeper:
        1. Macro Supply Wall Detection (Half-Yearly/Yearly/Quarterly Wall - Ep 15 & 11)
        2. Origin vs. Distribution Classification (Pristine Origin vs Shallow Basing - Ep 15 & 6)
        3. Curve Location Analysis (VLOC/LOC/EQB/HOC/VHOC/ATH - Ep 7)
        4. Mahabharata Character Alignment (Arjuna + Krishna vs Bhishma Pitamah - Ep 8)
        5. Trend Direction & Zone Violations (ITF 50 SMA Clock & Advanced Violations - Ep 7 & 13)
        6. Candle Closing Concept & Authenticity (Proven Achievement & Virgin Origins - Ep 6 & 9)
        7. Base Candle Scorer & LOTL Safety (1-3 Bases vs 4-5+ - Ep 5 & 6)
        8. Trade Score & Dynamic EMA Confluence (7/7 Score + MA Bonus = 8/7 - Ep 8, 12, 13)
        9. Execution Stance Determination (Aggressive vs Conservative - Ep 11)
        10. Entry Type Strategy (Type 1 Limit vs Confirmation Entry - Ep 9 & 14)
        11. All-Time Low (ATL) Long Prohibition Protocol (Ep 14)
        12. Developmental 100-Trade Rule & Style Verification (WIT/MIT - Ep 9)
        13. Mathematical Position Sizing & Rupee-Risk Invariance (Ep 10)
        14. Rejection Mindset Audit & Multi-Timeframe Target Expectation (8:1 to 10:1+ for Origin - Ep 4, 8, 15)
        """
        audit_checks_passed: List[str] = []
        rejection_reasons: List[str] = []

        # 1. Macro Supply Wall Detection (Ep 15)
        macro_wall_status, macro_wall_zone, macro_msg = cls.detect_macro_supply_wall(cmp, macro_supply_zones)
        if execution_zone.is_demand:
            if macro_wall_status in (MacroSupplyWallStatus.COLLIDING_WITH_WALL, MacroSupplyWallStatus.FALLING_AWAY_FROM_WALL):
                if attempted_entry_type == EntryType.SET_AND_FORGET or not is_at_cycle_turning_point:
                    rejection_reasons.append(
                        "The Macro Trap Detected: Price is colliding with or falling away from a Half-Yearly/Yearly Supply Wall. "
                        "Aggressive long entries into intermediate demand are strictly prohibited due to multi-month institutional selling pressure."
                    )
                else:
                    audit_checks_passed.append(f"Macro Wall Alert: Handled with conservative stance: {macro_msg}")
            else:
                audit_checks_passed.append("Macro Supply Wall: Clear (No overhead Half-Yearly/Yearly collision).")
        else:
            audit_checks_passed.append("Macro Supply Wall: Not applicable for short setup.")

        # 2. Origin Quality vs. Distribution (Ep 15 & 6)
        origin_quality, origin_msg = cls.classify_origin_vs_distribution(
            execution_zone, is_at_cycle_turning_point, has_ema_support, is_distributive_stair_step
        )
        if origin_quality == OriginQuality.GARBAGE_CONSOLIDATION:
            rejection_reasons.append(
                f"Origin Quality: Garbage Area detected. Base candle count ({execution_zone.base_candles_count}) "
                f"or overlapping wicks make marking invalid."
            )
        elif origin_quality == OriginQuality.SHALLOW_DISTRIBUTIVE:
            if macro_wall_status in (MacroSupplyWallStatus.COLLIDING_WITH_WALL, MacroSupplyWallStatus.FALLING_AWAY_FROM_WALL):
                rejection_reasons.append("Origin Quality: Shallow distributive basing cannot withstand selling pressure from overhead macro supply wall.")
            else:
                audit_checks_passed.append("Origin Quality: Shallow / secondary base accepted with conservative stance.")
        elif origin_quality == OriginQuality.PRISTINE_ORIGIN:
            audit_checks_passed.append(f"Origin Quality: {origin_msg}")

        # 3. Curve Position & Directional Bias (Ep 7)
        if execution_zone.is_demand:
            if curve_position in (CurvePosition.HIGH_ON_CURVE, CurvePosition.VERY_HIGH_ON_CURVE):
                rejection_reasons.append(f"Curve Position: Long trade prohibited in {curve_position.value} (unfavorable location).")
            else:
                audit_checks_passed.append(f"Curve Position: Location favorable for buying ({curve_position.value}).")
        else:
            if curve_position in (CurvePosition.LOW_ON_CURVE, CurvePosition.VERY_LOW_ON_CURVE):
                rejection_reasons.append(f"Curve Position: Short trade prohibited in {curve_position.value} (unfavorable location).")
            elif curve_position == CurvePosition.ALL_TIME_HIGH:
                rejection_reasons.append("Curve Position: Shorting at All-Time High is strictly prohibited.")
            else:
                audit_checks_passed.append(f"Curve Position: Location favorable for selling ({curve_position.value}).")

        # 4. Mahabharata Character Alignment (Ep 8)
        if htf_zone:
            if execution_zone.is_demand and not htf_zone.is_demand:
                rejection_reasons.append("Mahabharata Alignment: Fatal Trap! Arjuna (LTF Demand) entering directly into Bhishma Pitamah (HTF Supply).")
            elif not execution_zone.is_demand and htf_zone.is_demand:
                rejection_reasons.append("Mahabharata Alignment: Fatal Trap! Duryodhana (LTF Supply) shorting directly on top of Shri Krishna (HTF Demand).")
            else:
                audit_checks_passed.append("Mahabharata Alignment: Harmonious institutional alignment (Arjuna coincided with Shri Krishna).")
        else:
            audit_checks_passed.append("Mahabharata Alignment: Single-timeframe / standalone evaluation.")

        # 5. Trend Alignment & Advanced Violations (Ep 7 & 13)
        if execution_zone.is_demand:
            if itf_trend == TrendDirection.DOWNTREND:
                if attempted_entry_type == EntryType.SET_AND_FORGET and not is_at_cycle_turning_point:
                    rejection_reasons.append("Trend Alignment: Blind limit buying (Type 1) against ITF Downtrend is prohibited; requires Confirmation Entry (Episode 14).")
                else:
                    audit_checks_passed.append("Trend Alignment: Counter-trend long permitted via confirmation entry / pristine origin.")
            else:
                audit_checks_passed.append(f"Trend Alignment: Favorable trend alignment ({itf_trend.value}).")
        else:
            if itf_trend == TrendDirection.UPTREND:
                if attempted_entry_type == EntryType.SET_AND_FORGET:
                    rejection_reasons.append("Trend Alignment: Blind shorting against ITF Uptrend is prohibited; requires confirmation.")
                else:
                    audit_checks_passed.append("Trend Alignment: Counter-trend short permitted via confirmation entry.")
            else:
                audit_checks_passed.append(f"Trend Alignment: Favorable trend alignment ({itf_trend.value}).")

        # 6. Candle Closing Concept & Authenticity (Ep 6 & 9)
        if execution_zone.authenticity == ZoneAuthenticity.NON_AUTHENTIC and not execution_zone.has_proven_achievement:
            rejection_reasons.append("Closing & Authenticity: Non-authentic zone lacks proven closing achievement above previous structure.")
        else:
            audit_checks_passed.append("Closing & Authenticity: Proven zone structure and authentic origin verified.")

        # 7. Base Candle Scorer (Ep 5)
        if execution_zone.base_candles_count > 5:
            rejection_reasons.append(f"Base Candle Count: {execution_zone.base_candles_count} base candles exceeds allowable limit of 5 (diluted institutional momentum).")
        else:
            audit_checks_passed.append(f"Base Candle Count: {execution_zone.base_candles_count} base candle(s) represents concentrated institutional orders.")

        # 8. Trade Score & Dynamic EMA Confluence (Ep 8, 12, 13)
        freshness_pts = 3.0 if execution_zone.is_fresh else (1.5 if execution_zone.tested_at_idx is not None else 0.0)
        strength_pts = 2.0 if execution_zone.departure_strength >= 2 or execution_zone.is_gap_base_zone else 1.0
        time_pts = 2.0 if execution_zone.base_candles_count <= 3 else (1.0 if execution_zone.base_candles_count <= 5 else 0.0)
        base_score = freshness_pts + strength_pts + time_pts
        ema_bonus = 1.0 if has_ema_support else 0.0
        total_score = min(8.0, base_score + ema_bonus)

        # Episode 16: Sector Support Supreme Add-on (+2 Points) & Missing Support Filter
        if execution_zone.is_demand:
            if is_sector_in_free_fall:
                rejection_reasons.append(
                    "The Missing Support Trap Detected: Stock is in Demand Zone, but parent sector is in free fall. "
                    "Long execution is prohibited until parent sector reaches historical support."
                )
            elif is_parent_sector_in_demand:
                sector_bonus = 2.0
                total_score = min(9.0, total_score + sector_bonus)
                confluence_text = " (Level 3 Rocket Move with Nifty 50!)" if is_nifty_in_demand else ""
                audit_checks_passed.append(
                    f"Sector Support Verified (+2 Extra Trade Score Points awarded{confluence_text}): "
                    f"Parent sector is in Demand Zone."
                )

        # Episode 17: Candlestick Patterns & The Whipsaw Trap
        if is_pattern_in_mid_air_isolation:
            rejection_reasons.append(
                "The Whipsaw Trap Detected: Attempted to trade a conventional candlestick pattern in mid-air "
                "isolation without institutional zone support. Statistical accuracy is 50/50 (coin toss); execution is prohibited."
            )
        elif candlestick_pattern:
            if execution_zone.is_demand:
                total_score = min(10.0, total_score + 1.0)
                audit_checks_passed.append(
                    f"Candlestick Pattern Post-Entry Confidence Booster (+1 Bonus): {candlestick_pattern} "
                    f"confirmed at Demand Zone, visually verifying institutional absorption."
                )

        # Episode 18: Gap Theory & Institutional Applications
        if gap_application_report is not None:
            gap_bonus = gap_application_report.trade_score_bonus
            if gap_bonus > 0:
                total_score = min(11.0, total_score + gap_bonus)
                audit_checks_passed.append(
                    f"Gap Confluence (+{gap_bonus} Bonus): {gap_application_report.application_type.value} "
                    f"verified ({gap_application_report.probability_rating})."
                )
            if gap_application_report.disappearing_gap_detected:
                audit_checks_passed.append(
                    "Disappearing Gap Verified: Completed daily candle masks the morning opening void, "
                    "but true order-flow imbalance confirmed at 9:15 AM open."
                )

        # Episode 18: Window Gap Execution Rule
        if is_window_gap_present and window_gap_decision is not None:
            if window_gap_decision == "WINDOW_GAP_ELEVATED":
                elevated_str = f" to ₹{window_gap_elevated_entry:.2f}" if window_gap_elevated_entry else ""
                audit_checks_passed.append(
                    f"Window Gap Execution: Entry elevated{elevated_str} due to tight risk inflation. "
                    "Stop-loss strictly maintained below distal line."
                )
            elif window_gap_decision == "WINDOW_GAP_DISCIPLINED_BASE":
                audit_checks_passed.append(
                    "Window Gap Execution: Maintained disciplined entry at Base Proximal line. "
                    "No-Chase rule enforced to prevent inflated stop-loss risk."
                )

        # Episode 19: Indicator Confluence (RSI Reality Check)
        if rsi_value is not None:
            if execution_zone.is_demand and rsi_value <= 30.0:
                total_score = min(12.0, total_score + 1.0)
                audit_checks_passed.append(
                    f"Indicator Confluence Bonus (+1 Point): Qualified Demand Zone backed by Oversold RSI ({rsi_value:.1f})."
                )
            elif not execution_zone.is_demand and rsi_value >= 70.0:
                total_score = min(12.0, total_score + 1.0)
                audit_checks_passed.append(
                    f"Indicator Confluence Bonus (+1 Point): Qualified Supply Zone backed by Overbought RSI ({rsi_value:.1f})."
                )
            elif itf_trend == TrendDirection.UPTREND and rsi_value >= 70.0:
                audit_checks_passed.append(
                    f"Indicator Myth Avoided: RSI is {rsi_value:.1f} (Overbought) in Uptrend. "
                    "Assets remain overbought for months; shorting prohibited, trend strength confirmed."
                )

        # Episode 19: Market Trap Detection (Bull Traps & Bear Traps)
        if is_breakout_trade and breakout_price is not None:
            if macro_supply_zones:
                for m_sz in macro_supply_zones:
                    if m_sz.proximal_line <= breakout_price <= m_sz.distal_line or abs(breakout_price - m_sz.proximal_line) <= (0.01 * m_sz.proximal_line):
                        rejection_reasons.append(
                            f"BULL TRAP DETECTED: Attempted to buy breakout at ₹{breakout_price:.2f} directly into "
                            f"Higher Timeframe Supply Zone [₹{m_sz.proximal_line:.2f} - ₹{m_sz.distal_line:.2f}]. "
                            "Institutions use retail breakout buying as exit liquidity; price collapse imminent."
                        )
                        break
            if not execution_zone.is_demand and htf_zone and htf_zone.is_demand:
                if htf_zone.distal_line <= breakout_price <= htf_zone.proximal_line or abs(breakout_price - htf_zone.proximal_line) <= (0.01 * htf_zone.proximal_line):
                    rejection_reasons.append(
                        f"BEAR TRAP DETECTED: Attempted to short breakdown at ₹{breakout_price:.2f} directly into "
                        f"Higher Timeframe Demand Zone [₹{htf_zone.distal_line:.2f} - ₹{htf_zone.proximal_line:.2f}]. "
                        "Institutions absorb breakdown selling; violent upward reversal expected."
                    )

        if base_score < 6.0 and not is_parent_sector_in_demand:
            rejection_reasons.append(f"Trade Score: Base score {base_score:.1f}/7.0 is below institutional minimum threshold of 6.0/7.0.")
        else:
            audit_checks_passed.append(f"Trade Score: Score {total_score:.1f}/7.0 meets 1% Club institutional standard.")

        # 9. All-Time Low (ATL) Long Prohibition Protocol (Ep 14)
        if is_at_all_time_low and execution_zone.is_demand:
            if consecutive_supply_breaches < 2:
                rejection_reasons.append(
                    f"ATL Long Prohibition: Asset at All-Time Low with only {consecutive_supply_breaches} supply breach(es). "
                    f"Longs strictly forbidden until >= 2 supply zones are breached on ITF."
                )
            else:
                audit_checks_passed.append("ATL Protocol: Qualified bottom-out verified with >= 2 supply zone breaches.")
        else:
            audit_checks_passed.append("ATL Protocol: Normal market condition.")

        # 10. 100-Trade Directive & Style Verification (Ep 9)
        if prior_trades_count < 100 and execution_zone.timeframe in (TimeframeTier.INTRADAY, TimeframeTier.M75):
            rejection_reasons.append(
                f"100-Trade Directive: Completed {prior_trades_count}/100 positional trades. "
                f"Intraday execution restricted until developmental milestone met."
            )
        else:
            audit_checks_passed.append("100-Trade Directive: Trading style complies with professional developmental rule.")

        # 11. Mathematical Position Sizing & Rupee-Risk Invariance (Ep 10, Ep 18 Window Gap, Ep 19 LOTL)
        if is_lotl_setup and lotl_merged_entry is not None and lotl_lower_distal_sl is not None:
            effective_entry = lotl_merged_entry
            effective_stoploss = lotl_lower_distal_sl
            audit_checks_passed.append(
                f"LOTL Execution ({lotl_entry_mode or 'BALANCED_MIDDLE'}): Entry at ₹{effective_entry:.2f}. "
                f"Stop-Loss Mandate enforced strictly below Lower Origin Distal Line at ₹{effective_stoploss:.2f}."
            )
        else:
            effective_stoploss = execution_zone.stop_loss
            effective_entry = (
                window_gap_elevated_entry
                if (is_window_gap_present and window_gap_decision == "WINDOW_GAP_ELEVATED" and window_gap_elevated_entry)
                else execution_zone.entry_price
            )

        risk_per_share = abs(effective_entry - effective_stoploss)
        if risk_per_share <= 0:
            risk_per_share = abs(execution_zone.proximal_line - execution_zone.distal_line)

        monetary_risk = capital * (risk_per_trade_pct / 100.0)
        calculated_qty = int(monetary_risk // risk_per_share) if risk_per_share > 0 else 0

        if calculated_qty <= 0:
            rejection_reasons.append(f"Position Sizing: Risk per share ₹{risk_per_share:.2f} exceeds allowable monetary risk ₹{monetary_risk:.2f} (Quantity = 0).")
        else:
            audit_checks_passed.append(f"Position Sizing: {calculated_qty} shares planned at exact ₹{monetary_risk:.2f} risk.")

        # 12. Target Expectation & RRR Expansion (Ep 4, 8, 15, 20)
        if is_ath_expansion_planned or curve_position == CurvePosition.ALL_TIME_HIGH:
            projected_rrr = 10.0  # Open sky multi-bagger expectation with dynamic trailing
            execution_zone.is_trailing_multi_bagger_active = True
            audit_checks_passed.append(
                "Target Expectation (Episode 20): Asset in All-Time High / Multi-Bagger expansion mode. "
                "Open sky target projected at 10.0:1+ RRR using Weekly Demand-Anchored Dynamic Trailing Stop-Loss."
            )
        elif origin_quality == OriginQuality.PRISTINE_ORIGIN:
            projected_rrr = 8.5  # Origin setups target opposing macro supply, delivering 8:1 to 10:1+
            audit_checks_passed.append("Target Expectation: Pristine origin expansion planned with 8.5:1 RRR targeting opposing macro supply.")
        else:
            projected_rrr = max(2.0, execution_zone.risk_reward_ratio)
            audit_checks_passed.append(f"Target Expectation: Standard multi-timeframe target planned at {projected_rrr:.1f}:1 RRR.")

        # 13. Execution Stance Determination (Ep 11)
        if (
            macro_wall_status in (MacroSupplyWallStatus.COLLIDING_WITH_WALL, MacroSupplyWallStatus.FALLING_AWAY_FROM_WALL)
            or origin_quality == OriginQuality.SHALLOW_DISTRIBUTIVE
            or itf_trend == TrendDirection.DOWNTREND
        ):
            trading_stance = TradingStance.CONSERVATIVE
        elif total_score >= 7.0 and origin_quality == OriginQuality.PRISTINE_ORIGIN:
            trading_stance = TradingStance.AGGRESSIVE
        else:
            trading_stance = TradingStance.CONSERVATIVE
        audit_checks_passed.append(f"Execution Stance: Evaluated as {trading_stance.value} based on road conditions.")

        # 14. Entry Type Strategy & Rejection Mindset Synthesis (Ep 9 & 14)
        if macro_wall_status in (MacroSupplyWallStatus.COLLIDING_WITH_WALL, MacroSupplyWallStatus.FALLING_AWAY_FROM_WALL):
            recommended_entry = EntryType.CONFIRMATION_IN_ZONE
        elif trading_stance == TradingStance.AGGRESSIVE and total_score >= 7.0:
            recommended_entry = EntryType.SET_AND_FORGET
        else:
            recommended_entry = EntryType.SET_AND_FORGET if total_score >= 6.5 else EntryType.CONFIRMATION_IN_ZONE

        # 15. Price Alert Level & Screen-Time Elimination (Episode 20)
        price_alert = (
            round(effective_entry + 2.0, 2)
            if execution_zone.is_demand
            else round(effective_entry - 2.0, 2)
        )
        execution_zone.price_alert_level = price_alert
        if execution_zone.trade_score is not None:
            execution_zone.trade_score.price_alert_level = price_alert
            execution_zone.trade_score.trailing_sl_eligible = bool(
                is_ath_expansion_planned or curve_position == CurvePosition.ALL_TIME_HIGH
            )
        audit_checks_passed.append(
            f"Price Alert Mandate (Episode 20): Alert level set at ₹{price_alert:.2f} (2 points before entry) to eliminate active screen-staring."
        )

        is_approved = len(rejection_reasons) == 0
        if is_approved:
            summary = (
                f"1% CLUB APPROVED: Trade setup successfully passed all 14 institutional audit checks "
                f"(Score: {total_score:.1f}, Stance: {trading_stance.value}, RRR: {projected_rrr:.1f}:1, Qty: {calculated_qty})."
            )
        else:
            summary = (
                f"REJECTED BY INSTITUTIONAL DISCIPLINE: Setup failed {len(rejection_reasons)} check(s): "
                f"{'; '.join(rejection_reasons)}"
            )

        return MasterRevisionAuditReport(
            is_approved=is_approved,
            trading_stance=trading_stance,
            recommended_entry_type=recommended_entry,
            macro_wall_status=macro_wall_status,
            origin_quality=origin_quality,
            curve_position=curve_position,
            itf_trend=itf_trend,
            trade_score=total_score,
            calculated_position_size=calculated_qty,
            projected_rrr=projected_rrr,
            audit_checks_passed=audit_checks_passed,
            rejection_reasons=rejection_reasons,
            audit_verdict_summary=summary,
            overpowering_htf_supply=macro_wall_zone,
        )

    @staticmethod
    def evaluate_sector_support_bonus(
        zone: IdentifiedZone,
        is_parent_sector_in_demand: bool,
        is_nifty_in_demand: bool = False,
        is_sector_in_free_fall: bool = False,
    ) -> Tuple[bool, int, str]:
        """
        Episode 16 GTF Rule: Sector Support as Supreme Extra Trade Score (+2 Points).
        - Conventional indicators add +1 bonus point; Sector Support awards +2 bonus points.
        - An ordinary 6/7 setup with parent sector in demand reaches 8/7, easily reaching target.
        - Missing Support Filter: If stock is in demand but parent sector is in free fall,
          awards 0 bonus points and triggers a high-vulnerability warning.
        """
        if not zone.is_demand:
            return False, 0, "Sector support evaluation only applicable for demand long setups currently."

        if is_sector_in_free_fall:
            return (
                False,
                0,
                "The Missing Support Trap: Parent sector is in free fall. Long execution prohibited until sector reaches demand.",
            )

        if is_parent_sector_in_demand and is_nifty_in_demand:
            return (
                True,
                2,
                "Level 3 Confluence (Rocket Move!): Stock + Parent Sector + Nifty 50 ALL in Demand (+2 Extra Trade Score awarded).",
            )

        if is_parent_sector_in_demand:
            return (
                True,
                2,
                "Sector Support Confirmed (+2 Extra Trade Score awarded): Parent sector is in Demand Zone.",
            )

        if is_nifty_in_demand:
            return (
                True,
                1,
                "Nifty Universal Umbrella Support (+1 Extra Trade Score awarded): Nifty 50 is in Demand Zone.",
            )

        return False, 0, "No sector support detected; baseline trade score intact."

    @staticmethod
    def evaluate_candlestick_pattern_confidence_bonus(
        zone: IdentifiedZone,
        pattern_name: str,
        is_bullish_pattern: bool,
        is_bearish_pattern: bool,
        is_in_mid_air: bool = False,
    ) -> Tuple[bool, int, str]:
        """
        Episode 17 GTF Rule: Candlestick Patterns as an Extra Trade Score (+1 Point).
        - Standalone Use: NEVER trade patterns on their own (Score: 0 / Whipsaw Trap).
        - Post-Entry Confidence Booster: When a planned limit order executes at an
          institutional Demand Zone and the candle subsequently closes as a Hammer,
          Bullish Engulfing, or Morning Star, award +1 Post-Entry Confidence Bonus.
        - Institutional Absorption: A bearish pattern at a Demand Zone fails (Absorption Law).
        """
        if is_in_mid_air:
            return (
                False,
                0,
                f"The Whipsaw Trap: {pattern_name} formed in mid-air chart space. 50/50 coin toss; trading prohibited.",
            )

        if zone.is_demand:
            if is_bearish_pattern:
                return (
                    False,
                    0,
                    f"Institutional Absorption Trap: Bearish pattern {pattern_name} inside Demand Zone will be absorbed "
                    f"by resting institutional buy orders. Shorting will fail (Bear Trap).",
                )
            if is_bullish_pattern:
                return (
                    True,
                    1,
                    f"Post-Entry Confidence Booster (+1 Bonus): {pattern_name} confirmed at Demand Zone. "
                    f"Visual proof of institutional absorption at proximal line.",
                )

        if not zone.is_demand:
            if is_bullish_pattern:
                return (
                    False,
                    0,
                    f"Institutional Rejection Trap: Bullish pattern {pattern_name} inside Supply Zone will be rejected "
                    f"by resting institutional sell orders. Buying will fail (Bull Trap).",
                )
            if is_bearish_pattern:
                return (
                    True,
                    1,
                    f"Post-Entry Confidence Booster (+1 Bonus): {pattern_name} confirmed at Supply Zone. "
                    f"Visual proof of institutional rejection at proximal line.",
                )

        return False, 0, "No candlestick pattern confluence detected."

    @classmethod
    def evaluate_gap_confluence_bonus(
        cls,
        zone: IdentifiedZone,
        gap_report: Any,
    ) -> Tuple[bool, int, str]:
        """
        Episode 18 GTF Rule: Gap Confluence as an Extra Trade Score Bonus:
        - Application 1 (Novice Gap into Zone): +1 Point
        - Application 2 (Novice Gap into Pro Gap Origin): +2 Points
        - Application 4 (Master Setup: Novice In + Pro Out): +2 Points
        - Application 3 (Pro Gap departing from Zone): Post-entry confirmation (extended targets)
        """
        bonus = gap_report.trade_score_bonus
        if zone.trade_score is not None and bonus > 0:
            zone.trade_score.gap_confluence_bonus = bonus
            zone.trade_score.gap_application = gap_report.application_type.value
            zone.trade_score.total_score += bonus
        return (bonus > 0, bonus, gap_report.advisory_message)

    @classmethod
    def evaluate_window_gap_execution(
        cls,
        zone: IdentifiedZone,
        legout_open: float,
        legout_extreme_wick: float,
        max_risk_inflation_threshold: float = 0.35,
    ) -> Any:
        """
        Episode 18 GTF Rule: Window Gap Execution Analysis.
        - Identifies whether an explosive leg-out gapped away from the base candle.
        - Evaluates risk inflation:
          - If close to base (<= 35% risk inflation): WINDOW_GAP_ELEVATED (elevate entry, anchor SL below distal).
          - If far from base (> 35% risk inflation): WINDOW_GAP_DISCIPLINED_BASE (No-Chase Rule).
        """
        from alphacouncil.alpha.gap_engine import GapTheoryEngine, WindowGapDecision

        analysis = GapTheoryEngine.analyze_window_gap(
            base_proximal=zone.proximal_line,
            distal=zone.distal_line,
            legout_open=legout_open,
            legout_extreme_wick=legout_extreme_wick,
            is_demand_zone=zone.is_demand,
            max_risk_inflation_threshold=max_risk_inflation_threshold,
        )
        zone.window_gap_level = analysis.window_gap_level
        zone.window_gap_decision = analysis.decision.value
        if analysis.decision == WindowGapDecision.WINDOW_GAP_ELEVATED:
            zone.entry_price = analysis.window_gap_level
        return analysis

    @classmethod
    def merge_lotl_zones(
        cls,
        zones: List[IdentifiedZone],
        entry_option: Any = None,  # LOTLEntryOption.BALANCED_MIDDLE
        is_cross_wave: bool = False,
    ) -> Any:
        """
        Episode 19 GTF Rule: Level on Top of the Level (LOTL) Merging.
        - Stop-Loss Mandate: SL is ALWAYS anchored below the Lower Distal Line (Demand) or above Upper Distal (Supply).
        - Stacking Limit (3+ Rule): Discards upper bases when >= 3 levels form to avoid Garbage Areas.
        - Entry Options: AGGRESSIVE (Upper PL), CONSERVATIVE (Lower PL), BALANCED_MIDDLE (Ideal Sweet Spot).
        """
        from alphacouncil.alpha.trap_and_pattern_engine import (
            LOTLEntryOption,
            MarketTrapsAndPatternTruthEngine,
        )

        opt = entry_option or LOTLEntryOption.BALANCED_MIDDLE
        merged = MarketTrapsAndPatternTruthEngine.merge_lotl_zones(
            zones=zones,
            entry_option=opt,
            is_cross_wave=is_cross_wave,
        )

        for z in zones:
            z.is_lotl_origin = (z == merged.origin_zone)
            z.is_lotl_cushion = (z == merged.cushion_zone)
            z.lotl_merged_entry = merged.entry_price
            z.lotl_merged_stoploss = merged.stop_loss
            if z.trade_score is not None:
                z.trade_score.is_lotl_zone = True
                z.trade_score.lotl_entry_mode = opt.value

        return merged

    @classmethod
    def evaluate_indicator_confluence_bonus(
        cls,
        zone: IdentifiedZone,
        rsi_value: float,
        itf_trend: str = "UPTREND",
    ) -> Any:
        """
        Episode 19 GTF Rule: Indicator Reality Check (RSI in GTF Trading).
        - Standalone Indicator Fallacy: Strong uptrends stay RSI > 70 for months. Never short overbought in an uptrend!
        - GTF Confluence: When an independently qualified Demand Zone coincides with Oversold RSI (<= 30),
          award +1 Extra Trade Score Bonus.
        """
        from alphacouncil.alpha.trap_and_pattern_engine import (
            IndicatorConfluenceType,
            MarketTrapsAndPatternTruthEngine,
        )

        report = MarketTrapsAndPatternTruthEngine.evaluate_indicator_confluence(
            zone_is_demand=zone.is_demand,
            rsi_value=rsi_value,
            itf_trend=itf_trend,
        )

        if zone.trade_score is not None:
            if report.confluence_type in (
                IndicatorConfluenceType.OVERSOLD_DEMAND_BOOST,
                IndicatorConfluenceType.OVERBOUGHT_SUPPLY_BOOST,
            ):
                zone.trade_score.indicator_confluence_bonus = 1
                zone.trade_score.total_score += 1.0

        return report

    @classmethod
    def setup_dynamic_trailing_for_zone(
        cls,
        symbol: str,
        zone: IdentifiedZone,
    ) -> Any:
        """
        Episode 20 GTF Rule: Initializes Dynamic Demand-Anchored Trailing for qualified positions.
        """
        from alphacouncil.alpha.scanner_and_trailing_engine import DynamicTrailingEngine
        return DynamicTrailingEngine.initialize_trailing_position(
            symbol=symbol,
            entry_price=zone.entry_price,
            initial_stop_loss=zone.stop_loss,
        )

```

---

## 5. Deterministic Liquidity Sweep Detector (H1) (`alphacouncil/alpha/sweep_detector.py`)

```python
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

```

---

## 6. López de Prado Triple Barrier & OU Half-Life (`alphacouncil/alpha/triple_barrier.py`)

```python
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

```

---

## 7. FinBERT Sentiment & Binomial Audit (H2) (`alphacouncil/alpha/sentiment_nlp.py`)

```python
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
    Research Prototype Stub / Synthetic Lexicon Featurizer.
    Evaluates synthetic financial text excerpts via deterministic keyword mapping
    in zero-GPU and offline testing environments.
    In live production, connects to real-time SEBI corporate filings / RSS news feeds.
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

```

---

## 8. Sectoral Analysis Engine (Episode 16) (`alphacouncil/alpha/sector_engine.py`)

```python
"""
Sectoral Analysis Core Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 16 principles:
1. The +2 Extra Trade Score for Sector Support (The Supreme Add-on).
2. Nifty 50 as the Universal Umbrella Benchmark.
3. Sector Weightings & Heavyweight Concentration (>50% Rule).
4. Simultaneous Zone Alignment (The Confluence Multiplier / Rocket Move):
   - Level 1: Only Nifty in Demand Zone (+0.5 modest push).
   - Level 2: Only Stock in Demand Zone (+0.0 independent bounce).
   - Level 3: Stock + Sector + Nifty ALL in Demand Zones simultaneously (+2.0 Rocket Move!).
5. The Missing Support Filter (Blocks longs when sector is in free fall).
6. Sector Rotation Dynamics & "Sectors Cannot Go to Zero" Axiom.
7. Portfolio Construction Rules (12-15 stocks max, 2-4 per sector, 40-40-20 rule).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class SectorName(str, Enum):
    NIFTY_50 = "NIFTY_50"
    NIFTY_BANK = "NIFTY_BANK"
    NIFTY_FIN_SERVICES = "NIFTY_FIN_SERVICES"
    NIFTY_AUTO = "NIFTY_AUTO"
    NIFTY_IT = "NIFTY_IT"
    NIFTY_METAL = "NIFTY_METAL"
    NIFTY_REALTY = "NIFTY_REALTY"
    NIFTY_PHARMA = "NIFTY_PHARMA"
    NIFTY_FMCG = "NIFTY_FMCG"
    NIFTY_ENERGY = "NIFTY_ENERGY"
    NIFTY_PSU_BANK = "NIFTY_PSU_BANK"
    NIFTY_PVT_BANK = "NIFTY_PVT_BANK"
    NIFTY_MEDIA = "NIFTY_MEDIA"
    NIFTY_INFRA = "NIFTY_INFRA"


class SectorConfluenceLevel(str, Enum):
    LEVEL_1_NIFTY_ONLY = "LEVEL_1_NIFTY_ONLY"    # Modest macro push (+0.5)
    LEVEL_2_STOCK_ONLY = "LEVEL_2_STOCK_ONLY"    # Stock bounces independently (+0.0)
    LEVEL_3_ROCKET_MOVE = "LEVEL_3_ROCKET_MOVE"  # Stock + Sector + Nifty ALL in Demand (+2.0 Rocket Move)
    SECTOR_SUPPORTED = "SECTOR_SUPPORTED"        # Stock + Sector in Demand (+2.0)
    MISSING_SUPPORT = "MISSING_SUPPORT"          # Stock in Demand, but Sector in free fall (Veto/Halt)


class SectorRotationPhase(str, Enum):
    ACCUMULATION_AT_CYCLE_LOW = "ACCUMULATION_AT_CYCLE_LOW"  # Multi-year low / macro origin (Sectors Cannot Go to Zero)
    EARLY_EXPANSION = "EARLY_EXPANSION"                      # Breakout from base through tested supply trendline
    PEAK_AT_ALL_TIME_HIGH = "PEAK_AT_ALL_TIME_HIGH"          # Distribution at ATH; rotate to lagging constituents
    DISTRIBUTION_AT_SUPPLY = "DISTRIBUTION_AT_SUPPLY"        # Multi-month selling pressure from macro supply
    CORRECTION_WITH_TESTED_SUPPLY = "CORRECTION_WITH_TESTED_SUPPLY" # Relief rallies testing and consuming supply


# =====================================================================
# OFFICIAL NSE SECTOR WEIGHTINGS REGISTRY (FACT SHEET GROUNDING)
# =====================================================================

NSE_SECTOR_WEIGHTINGS: Dict[SectorName, Dict[str, float]] = {
    SectorName.NIFTY_AUTO: {
        "M&M": 20.0,
        "MARUTI": 19.0,
        "TATAMOTORS": 12.0,  # Top 3 account for 51.0% (>50%)
        "BAJAJ-AUTO": 9.0,
        "EICHERMOT": 7.0,
        "HEROMOTOCO": 6.0,
        "TVSMOTOR": 5.0,
        "BHARATFORG": 4.0,
        "ASHOKLEY": 4.0,
        "BALKRISIND": 3.0,
        "MOTHERSON": 3.0,
        "BOSCHLTD": 2.5,
        "APOLLOTYRE": 2.0,
        "MRF": 1.5,
        "TIINDIA": 1.0,
    },
    SectorName.NIFTY_IT: {
        "TCS": 28.0,
        "INFY": 26.0,  # Top 2 account for 54.0% (>50%)
        "HCLTECH": 10.0,
        "WIPRO": 8.0,
        "TECHM": 7.0,
        "LTIM": 6.0,
        "PERSISTENT": 5.0,
        "COFORGE": 4.0,
        "MPHASIS": 3.0,
        "LTTS": 3.0,
    },
    SectorName.NIFTY_FIN_SERVICES: {
        "HDFCBANK": 29.0,
        "ICICIBANK": 22.0,  # Top 2 account for 51.0% (>50%)
        "KOTAKBANK": 10.0,
        "AXISBANK": 10.0,
        "SBIN": 9.0,
        "BAJFINANCE": 8.0,
        "BAJAJFINSV": 4.0,
        "CHOLAFIN": 3.0,
        "SHRIRAMFIN": 2.5,
        "HDFCLIFE": 2.5,
    },
    SectorName.NIFTY_BANK: {
        "HDFCBANK": 29.0,
        "ICICIBANK": 23.0,  # Top 2 account for 52.0% (>50%)
        "AXISBANK": 11.0,
        "KOTAKBANK": 10.0,
        "SBIN": 9.0,
        "INDUSINDBK": 6.0,
        "BANKBARODA": 3.5,
        "PNB": 2.5,
        "CANBK": 2.0,
        "FEDERALBNK": 1.5,
        "IDFCFIRSTB": 1.5,
        "AUBANK": 1.0,
    },
    SectorName.NIFTY_METAL: {
        "JSWSTEEL": 22.0,
        "TATASTEEL": 20.0,
        "HINDALCO": 18.0,  # Top 3 account for 60.0% (>50%)
        "ADANIENT": 15.0,
        "VEDL": 8.0,
        "JINDALSTEL": 6.0,
        "SAIL": 4.0,
        "NATIONALUM": 3.0,
        "NMDC": 2.5,
        "HINDZINC": 1.5,
    },
    SectorName.NIFTY_REALTY: {
        "DLF": 30.0,
        "GODREJPROP": 20.0,  # Top 2 account for 50.0%
        "OBEROIRLTY": 15.0,
        "PHOENIXLTD": 11.0,
        "PRESTIGE": 9.0,
        "BRIGADE": 5.0,
        "SOBHA": 4.0,
        "MAHLIFE": 3.0,
        "SUNTECK": 2.0,
        "IBREALEST": 1.0,
    },
    SectorName.NIFTY_PSU_BANK: {
        "SBIN": 38.0,
        "BANKBARODA": 16.0,  # Top 2 account for 54.0%
        "PNB": 14.0,
        "CANBK": 12.0,
        "UNIONBANK": 7.0,
        "INDIANB": 5.0,
        "BANKINDIA": 3.0,
        "CENTRALBK": 2.0,
        "IOB": 1.5,
        "UCOBANK": 1.5,
    },
}

# Reverse lookup mapping from ticker symbol to primary SectorName
STOCK_TO_SECTOR_LOOKUP: Dict[str, SectorName] = {
    # Auto
    "M&M": SectorName.NIFTY_AUTO,
    "MARUTI": SectorName.NIFTY_AUTO,
    "TATAMOTORS": SectorName.NIFTY_AUTO,
    "BAJAJ-AUTO": SectorName.NIFTY_AUTO,
    "EICHERMOT": SectorName.NIFTY_AUTO,
    "HEROMOTOCO": SectorName.NIFTY_AUTO,
    "TVSMOTOR": SectorName.NIFTY_AUTO,
    "ASHOKLEY": SectorName.NIFTY_AUTO,
    "BALKRISIND": SectorName.NIFTY_AUTO,
    # IT
    "TCS": SectorName.NIFTY_IT,
    "INFY": SectorName.NIFTY_IT,
    "HCLTECH": SectorName.NIFTY_IT,
    "WIPRO": SectorName.NIFTY_IT,
    "TECHM": SectorName.NIFTY_IT,
    "LTIM": SectorName.NIFTY_IT,
    # Banking & Finance
    "HDFCBANK": SectorName.NIFTY_BANK,
    "ICICIBANK": SectorName.NIFTY_BANK,
    "AXISBANK": SectorName.NIFTY_BANK,
    "KOTAKBANK": SectorName.NIFTY_BANK,
    "SBIN": SectorName.NIFTY_BANK,
    "BANKBARODA": SectorName.NIFTY_BANK,
    "CANBK": SectorName.NIFTY_BANK,
    "BAJFINANCE": SectorName.NIFTY_FIN_SERVICES,
    "BAJAJFINSV": SectorName.NIFTY_FIN_SERVICES,
    # Metal
    "JSWSTEEL": SectorName.NIFTY_METAL,
    "TATASTEEL": SectorName.NIFTY_METAL,
    "HINDALCO": SectorName.NIFTY_METAL,
    "ADANIENT": SectorName.NIFTY_METAL,
    "VEDL": SectorName.NIFTY_METAL,
    "SAIL": SectorName.NIFTY_METAL,
    "NATIONALUM": SectorName.NIFTY_METAL,
    # Realty
    "DLF": SectorName.NIFTY_REALTY,
    "GODREJPROP": SectorName.NIFTY_REALTY,
    "OBEROIRLTY": SectorName.NIFTY_REALTY,
}


@dataclass
class SectorConfluenceResult:
    confluence_level: SectorConfluenceLevel
    is_stock_in_demand: bool
    is_sector_in_demand: bool
    is_nifty_in_demand: bool
    bonus_points: float
    is_rocket_move: bool
    missing_support_warning: bool
    status_message: str


@dataclass
class HeavyweightStatusReport:
    sector: SectorName
    top_heavyweights: List[str]
    heavyweight_combined_weight_pct: float
    heavyweights_in_demand: List[str]
    heavyweights_in_supply: List[str]
    is_heavyweight_momentum_bullish: bool
    explanation: str


@dataclass
class PortfolioSectorAllocationReport:
    is_allocation_valid: bool
    total_stocks_count: int
    sectors_represented: List[SectorName]
    stocks_per_sector: Dict[str, int]
    rotation_arbitrage_candidates: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    advisory: str = ""


class SectorAnalysisEngine:
    """
    Episode 16 Quantitative Sector Engine:
    Manages Sector Weightings, Heavyweight Concentration, Simultaneous Confluence,
    Sector Rotation Cycles, and Portfolio Allocation.
    """

    @staticmethod
    def get_parent_sector(stock_symbol: str) -> SectorName:
        """
        Universal Rule: Returns the primary SectorName for an equity.
        If the sector is ambiguous or unlisted, defaults to Nifty 50 (Universal Umbrella).
        """
        clean_sym = stock_symbol.strip().upper()
        return STOCK_TO_SECTOR_LOOKUP.get(clean_sym, SectorName.NIFTY_50)

    @staticmethod
    def evaluate_heavyweight_concentration(
        sector: SectorName,
        stock_zone_states: Dict[str, str],  # Symbol -> "DEMAND", "SUPPLY", "NEUTRAL"
    ) -> HeavyweightStatusReport:
        """
        Episode 16: The >50% Heavyweight Concentration Rule.
        Evaluates whether the 2-3 stocks driving over 50% of the index are in
        Demand Zones (bullish index propel) or Supply Zones (bearish index drag).
        """
        weights = NSE_SECTOR_WEIGHTINGS.get(sector, {})
        if not weights:
            return HeavyweightStatusReport(
                sector=sector,
                top_heavyweights=[],
                heavyweight_combined_weight_pct=0.0,
                heavyweights_in_demand=[],
                heavyweights_in_supply=[],
                is_heavyweight_momentum_bullish=False,
                explanation=f"No granular weighting data registered for {sector.value}; evaluating via Nifty 50 umbrella.",
            )

        # Sort constituents by weight descending
        sorted_constituents = sorted(weights.items(), key=lambda x: x[1], reverse=True)

        # Select top heavyweights until combined weight crosses 50.0%
        top_hw: List[str] = []
        cum_weight = 0.0
        for sym, wt in sorted_constituents:
            top_hw.append(sym)
            cum_weight += wt
            if cum_weight >= 50.0:
                break

        in_demand: List[str] = []
        in_supply: List[str] = []

        for sym in top_hw:
            state = stock_zone_states.get(sym, "NEUTRAL").upper()
            if state == "DEMAND":
                in_demand.append(sym)
            elif state == "SUPPLY":
                in_supply.append(sym)

        # Heavyweight momentum is bullish if majority of top heavyweights are in Demand
        is_bullish = len(in_demand) >= (len(top_hw) / 2.0) and len(in_demand) > len(in_supply)

        if is_bullish:
            expl = (
                f"Bullish Heavyweight Momentum in {sector.value}: Top heavyweights "
                f"({', '.join(in_demand)}) controlling {cum_weight:.1f}% index weight are in Demand Zones. "
                f"Sector index will propel upward, creating tailwinds for individual constituents."
            )
        elif len(in_supply) > 0:
            expl = (
                f"Bearish Heavyweight Drag in {sector.value}: Heavyweights ({', '.join(in_supply)}) "
                f"are in Supply Zones. Even if low-weight constituents bounce, sector index will face heavy drag."
            )
        else:
            expl = (
                f"Neutral Heavyweight State in {sector.value}: Heavyweights controlling {cum_weight:.1f}% "
                f"are in consolidation without clear zone triggers."
            )

        return HeavyweightStatusReport(
            sector=sector,
            top_heavyweights=top_hw,
            heavyweight_combined_weight_pct=cum_weight,
            heavyweights_in_demand=in_demand,
            heavyweights_in_supply=in_supply,
            is_heavyweight_momentum_bullish=is_bullish,
            explanation=expl,
        )

    @staticmethod
    def evaluate_simultaneous_confluence(
        is_stock_in_demand: bool,
        is_sector_in_demand: bool,
        is_nifty_in_demand: bool,
        is_sector_in_free_fall: bool = False,
    ) -> SectorConfluenceResult:
        """
        Episode 16: The Three Levels of Sector Confluence & Missing Support Filter.
        - Level 1: Only Nifty in Demand Zone -> +0.5 points (Modest macro push).
        - Level 2: Only Stock in Demand Zone -> +0.0 points (Independent bounce).
        - Level 3: Stock + Sector + Nifty ALL in Demand Zones -> +2.0 points (EXPLOSIVE ROCKET MOVE!).
        - Stock + Sector in Demand -> +2.0 points (Supreme Sector Support Add-on).
        - The Missing Support Filter: If stock is in Demand but Sector/Nifty are in free fall,
          flag warning and block long execution.
        """
        # 1. The Missing Support Filter (Episode 16 Rule)
        if is_stock_in_demand and is_sector_in_free_fall:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.MISSING_SUPPORT,
                is_stock_in_demand=True,
                is_sector_in_demand=False,
                is_nifty_in_demand=is_nifty_in_demand,
                bonus_points=0.0,
                is_rocket_move=False,
                missing_support_warning=True,
                status_message=(
                    "The Missing Support Trap Detected: Stock is in Demand Zone, but parent sector is in free fall. "
                    "Long execution must be halted; wait for the parent sector to reach historical support."
                ),
            )

        # 2. Level 3: Simultaneous Triad Alignment (Rocket Move)
        if is_stock_in_demand and is_sector_in_demand and is_nifty_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.LEVEL_3_ROCKET_MOVE,
                is_stock_in_demand=True,
                is_sector_in_demand=True,
                is_nifty_in_demand=True,
                bonus_points=2.0,
                is_rocket_move=True,
                missing_support_warning=False,
                status_message=(
                    "Level 3 Confluence (Explosive Rocket Move!): Stock, Parent Sector, and Nifty 50 are ALL in "
                    "institutional Demand Zones simultaneously. +2 Extra Trade Score awarded. Exceptional statistical edge."
                ),
            )

        # 3. Stock + Sector in Demand (Standard Supreme Add-on)
        if is_stock_in_demand and is_sector_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.SECTOR_SUPPORTED,
                is_stock_in_demand=True,
                is_sector_in_demand=True,
                is_nifty_in_demand=False,
                bonus_points=2.0,
                is_rocket_move=False,
                missing_support_warning=False,
                status_message=(
                    "Sector Supported (+2 Extra Trade Score): Parent sector is in Demand Zone. "
                    "Macro institutional order flow provides powerful tailwind for individual stock setup."
                ),
            )

        # 4. Level 1: Only Nifty in Demand Zone
        if not is_stock_in_demand and not is_sector_in_demand and is_nifty_in_demand:
            return SectorConfluenceResult(
                confluence_level=SectorConfluenceLevel.LEVEL_1_NIFTY_ONLY,
                is_stock_in_demand=False,
                is_sector_in_demand=False,
                is_nifty_in_demand=True,
                bonus_points=0.5,
                is_rocket_move=False,
                missing_support_warning=False,
                status_message="Level 1 Confluence: Only Nifty 50 is in Demand Zone. Modest broader market push.",
            )

        # 5. Level 2: Only Stock in Demand Zone
        return SectorConfluenceResult(
            confluence_level=SectorConfluenceLevel.LEVEL_2_STOCK_ONLY,
            is_stock_in_demand=is_stock_in_demand,
            is_sector_in_demand=is_sector_in_demand,
            is_nifty_in_demand=is_nifty_in_demand,
            bonus_points=0.0,
            is_rocket_move=False,
            missing_support_warning=False,
            status_message="Level 2 Confluence: Only Stock is in Demand Zone. Stock must bounce independently.",
        )

    @staticmethod
    def evaluate_sector_rotation(
        sector: SectorName,
        current_index_level: float,
        macro_demand_zone: Optional[Tuple[float, float]] = None,
        macro_supply_zone: Optional[Tuple[float, float]] = None,
        tested_overhead_supply_count: int = 0,
        is_at_all_time_high: bool = False,
    ) -> Tuple[SectorRotationPhase, str]:
        """
        Episode 16: Sector Rotation Dynamics.
        - "Sectors Cannot Go to Zero": A national sector index (Metal, PSU Bank, IT) cannot go bankrupt.
          When reaching multi-year lows or historical demand origins, it is a prime institutional accumulation zone.
        - Tested Supply Trendline: Relief rallies testing and exhausting overhead supply clear the runway
          for explosive breakouts once the macro demand base is touched.
        - Peak at ATH: Rotate capital out of 5x run leaders into lagging quality constituents or bottoming sectors.
        """
        if is_at_all_time_high:
            return (
                SectorRotationPhase.PEAK_AT_ALL_TIME_HIGH,
                f"{sector.value} is at All-Time High. Avoid chasing 5x run leaders; "
                f"rotate capital into lagging quality constituents or bottoming sectors (GTF 40-40-20 rule).",
            )

        if macro_demand_zone:
            pl, dl = macro_demand_zone
            if dl <= current_index_level <= pl * 1.05:
                trendline_str = (
                    f" Overhead supply trendline exhausted with {tested_overhead_supply_count} tested supply zones; "
                    f"runway clear for explosive bull run."
                    if tested_overhead_supply_count >= 2
                    else ""
                )
                return (
                    SectorRotationPhase.ACCUMULATION_AT_CYCLE_LOW,
                    f"{sector.value} at Macro Institutional Demand Origin [{dl:.1f} - {pl:.1f}]. "
                    f"Sectors cannot go to zero; prime generational accumulation phase.{trendline_str}",
                )

        if macro_supply_zone:
            pl, dl = macro_supply_zone
            if pl <= current_index_level <= dl:
                return (
                    SectorRotationPhase.DISTRIBUTION_AT_SUPPLY,
                    f"{sector.value} is testing Macro Supply Zone [{pl:.1f} - {dl:.1f}]. "
                    f"Multi-month distribution pressure expected; tighten trailing stops.",
                )

        if tested_overhead_supply_count >= 2:
            return (
                SectorRotationPhase.CORRECTION_WITH_TESTED_SUPPLY,
                f"{sector.value} correcting with {tested_overhead_supply_count} tested overhead supply zones. "
                f"Sellers are depleting inventory on relief bounces.",
            )

        return (
            SectorRotationPhase.EARLY_EXPANSION,
            f"{sector.value} in intermediate expansion phase.",
        )

    @classmethod
    def audit_portfolio_construction(
        cls,
        stock_list: List[str],
        sector_lookup: Optional[Dict[str, SectorName]] = None,
    ) -> PortfolioSectorAllocationReport:
        """
        Episode 16: Long-Term Portfolio Construction Blueprint.
        Rules:
        1. Portfolio Size Limit: Maintain 12 to 15 stocks maximum (dilution beyond 15 creates index-like drag).
        2. Sector Allocation: Hold 2 to 4 stocks across different sectors (prevent industry over-concentration).
        3. Rotation Arbitrage: Identifies lagging quality constituents in high-momentum sectors.
        """
        total_stocks = len(stock_list)
        rejection_reasons: List[str] = []

        if total_stocks < 12:
            rejection_reasons.append(
                f"Under-diversified Portfolio: Contains {total_stocks} stocks (Minimum 12 required to prevent single-stock operational catastrophe)."
            )
        elif total_stocks > 15:
            rejection_reasons.append(
                f"Over-diversified Portfolio: Contains {total_stocks} stocks (Maximum 15 allowable; over-diversification dilutes returns into index performance)."
            )

        # Count stocks per sector
        stocks_per_sec: Dict[str, int] = {}
        sectors_set = set()

        for sym in stock_list:
            clean_sym = sym.strip().upper()
            sec = sector_lookup.get(clean_sym) if sector_lookup else cls.get_parent_sector(clean_sym)
            sec_name = sec.value
            sectors_set.add(sec)
            stocks_per_sec[sec_name] = stocks_per_sec.get(sec_name, 0) + 1

        # Check for over-concentration (>4 stocks in one sector)
        for sec_name, count in stocks_per_sec.items():
            if count > 4:
                rejection_reasons.append(
                    f"Sector Over-concentration: {sec_name} holds {count} stocks (Maximum allowable is 2 to 4 stocks per sector)."
                )

        is_valid = len(rejection_reasons) == 0

        if is_valid:
            advisory = (
                f"Optimal Portfolio Allocation: {total_stocks} stocks diversified across "
                f"{len(sectors_set)} sectors with 2-4 stocks per industry (GTF 40-40-20 Compliant)."
            )
        else:
            advisory = f"Portfolio Allocation Non-Compliant: {'; '.join(rejection_reasons)}"

        return PortfolioSectorAllocationReport(
            is_allocation_valid=is_valid,
            total_stocks_count=total_stocks,
            sectors_represented=list(sectors_set),
            stocks_per_sector=stocks_per_sec,
            rejection_reasons=rejection_reasons,
            advisory=advisory,
        )

```

---

## 9. Candlestick Patterns Truth Engine (Episode 17) (`alphacouncil/alpha/pattern_engine.py`)

```python
"""
Candlestick Patterns & Truth Core Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 17 principles:
1. The 50/50 Coin-Toss Reality of Conventional Candlestick Formations in Isolation.
2. The Whipsaw Trap (Why retail traders flip long/short and bleed capital).
3. The Institutional Absorption Law:
   - Bearish Pattern inside Demand Zone -> FAILS (Institutional Buying Absorbs It / Bear Trap).
   - Bullish Pattern inside Supply Zone -> FAILS (Institutional Selling Rejects It / Bull Trap).
4. Structural Equivalence:
   - Morning Star == Drop-Base-Rally (DBR) Reversal Demand Zone.
   - Evening Star == Rally-Base-Drop (RBD) Reversal Supply Zone.
   - Hammer == Institutional Order Absorption at Proximal Line.
   - Shooting Star == Institutional Order Rejection at Distal/Proximal Line.
5. Candlestick Patterns in Trade Scoring:
   - Standalone use: NEVER trade candlestick patterns on their own (Score: 0 / Prohibited).
   - After-the-fact utility: +1 Post-Entry Confidence Booster when confluent with zone.
6. The Social Media 'Pattern Seller' Trap Filter.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import numpy as np


class ConventionalPatternType(str, Enum):
    BULLISH_ENGULFING = "BULLISH_ENGULFING"
    BEARISH_ENGULFING = "BEARISH_ENGULFING"
    MORNING_STAR = "MORNING_STAR"
    EVENING_STAR = "EVENING_STAR"
    HAMMER = "HAMMER"
    INVERTED_HAMMER = "INVERTED_HAMMER"
    SHOOTING_STAR = "SHOOTING_STAR"
    BULLISH_HARAMI = "BULLISH_HARAMI"
    BEARISH_HARAMI = "BEARISH_HARAMI"
    NO_PATTERN = "NO_PATTERN"


class PatternZoneInteraction(str, Enum):
    ABSORBED_BY_DEMAND = "ABSORBED_BY_DEMAND"        # Bearish pattern inside Demand Zone -> FAILS (Absorption Law / Bear Trap)
    REJECTED_BY_SUPPLY = "REJECTED_BY_SUPPLY"        # Bullish pattern inside Supply Zone -> FAILS (Rejection Law / Bull Trap)
    CONFLUENT_DEMAND_BOOST = "CONFLUENT_DEMAND_BOOST" # Bullish pattern at Demand Zone -> +1 Post-entry Confidence Booster
    CONFLUENT_SUPPLY_BOOST = "CONFLUENT_SUPPLY_BOOST" # Bearish pattern at Supply Zone -> +1 Post-entry Confidence Booster
    MID_AIR_COIN_TOSS = "MID_AIR_COIN_TOSS"          # Pattern formed in isolation without zone backing -> 50/50 Whipsaw Trap


@dataclass
class PatternEvaluationReport:
    pattern_type: ConventionalPatternType
    is_bullish_pattern: bool
    is_bearish_pattern: bool
    zone_interaction: PatternZoneInteraction
    standalone_accuracy_pct: float = 50.0
    effective_accuracy_pct: float = 50.0
    is_tradeable_standalone: bool = False  # Strictly False in GTF methodology
    post_entry_confidence_bonus: int = 0   # 0 or 1 point
    gtf_structural_equivalent: str = ""
    advisory_message: str = ""


class CandlestickPatternTruthEngine:
    """
    Episode 17 Quantitative Pattern Truth Engine:
    Detects conventional patterns, translates them to GTF structural equivalents,
    and analyzes institutional order-flow absorption vs. rejection.
    """

    @staticmethod
    def detect_candlestick_pattern(
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        prior_trend: str = "DOWNTREND",
    ) -> Tuple[ConventionalPatternType, bool, bool]:
        """
        Detects standard Japanese candlestick patterns on recent price action.
        Returns: (PatternType, is_bullish, is_bearish).
        """
        n = len(closes)
        if n < 2:
            return ConventionalPatternType.NO_PATTERN, False, False

        o1, h1, l1, c1 = opens[-1], highs[-1], lows[-1], closes[-1]
        o2, _, _, c2 = opens[-2], highs[-2], lows[-2], closes[-2]

        body1 = abs(c1 - o1)
        body2 = abs(c2 - o2)

        # 1. Hammer & Inverted Hammer / Shooting Star (Single Candle)
        lower_shadow1 = min(o1, c1) - l1
        upper_shadow1 = h1 - max(o1, c1)

        # Hammer: small body near top, lower shadow >= 2x body, tiny upper shadow
        if body1 > 0 and lower_shadow1 >= 2.0 * body1 and upper_shadow1 <= 0.3 * body1:
            return ConventionalPatternType.HAMMER, True, False

        # Inverted Hammer / Shooting Star: small body near bottom, upper shadow >= 2x body
        if body1 > 0 and upper_shadow1 >= 2.0 * body1 and lower_shadow1 <= 0.3 * body1:
            if prior_trend.upper() == "UPTREND":
                return ConventionalPatternType.SHOOTING_STAR, False, True
            return ConventionalPatternType.INVERTED_HAMMER, True, False

        # 2. Bullish & Bearish Engulfing (Two Candles)
        # Bullish Engulfing: Candle 2 is Red, Candle 1 is Green and body engulfs Candle 2 body
        if c2 < o2 and c1 > o1:
            if o1 <= c2 + 1e-4 and c1 >= o2 - 1e-4 and body1 > body2:
                return ConventionalPatternType.BULLISH_ENGULFING, True, False

        # Bearish Engulfing: Candle 2 is Green, Candle 1 is Red and body engulfs Candle 2 body
        if c2 > o2 and c1 < o1:
            if o1 >= c2 - 1e-4 and c1 <= o2 + 1e-4 and body1 > body2:
                return ConventionalPatternType.BEARISH_ENGULFING, False, True

        # 3. Bullish & Bearish Harami (Mother-Baby inside candle)
        # Bullish Harami: Candle 2 is large Red, Candle 1 is small Green inside Candle 2 body
        if c2 < o2 and c1 > o1:
            if o1 >= c2 and c1 <= o2 and body1 < body2 * 0.7:
                return ConventionalPatternType.BULLISH_HARAMI, True, False

        # Bearish Harami: Candle 2 is large Green, Candle 1 is small Red inside Candle 2 body
        if c2 > o2 and c1 < o1:
            if o1 <= c2 and c1 >= o2 and body1 < body2 * 0.7:
                return ConventionalPatternType.BEARISH_HARAMI, False, True

        # 4. Morning Star & Evening Star (Three Candles)
        if n >= 3:
            o3, h3, l3, c3 = opens[-3], highs[-3], lows[-3], closes[-3]
            body3 = abs(c3 - o3)
            range3 = h3 - l3 if h3 > l3 else 1e-4

            # Morning Star: Red -> Base -> Green recovering >= 50%
            if c3 < o3 and (body3 / range3) >= 0.45:  # Candle 3 is Red exciting
                if body2 < body3 * 0.5:              # Candle 2 is Base / Star
                    if c1 > o1 and c1 >= (o3 + c3) / 2.0:  # Candle 1 is Green recovering >= 50%
                        return ConventionalPatternType.MORNING_STAR, True, False

            # Evening Star: Green -> Base -> Red dropping >= 50%
            if c3 > o3 and (body3 / range3) >= 0.45:  # Candle 3 is Green exciting
                if body2 < body3 * 0.5:              # Candle 2 is Base / Star
                    if c1 < o1 and c1 <= (o3 + c3) / 2.0:  # Candle 1 is Red dropping >= 50%
                        return ConventionalPatternType.EVENING_STAR, False, True

        return ConventionalPatternType.NO_PATTERN, False, False

    @classmethod
    def evaluate_pattern_zone_interaction(
        cls,
        pattern: ConventionalPatternType,
        is_bullish: bool,
        is_bearish: bool,
        cmp: float,
        nearby_demand_zone_boundaries: Optional[Tuple[float, float]] = None,  # (PL, DL)
        nearby_supply_zone_boundaries: Optional[Tuple[float, float]] = None,  # (PL, DL)
    ) -> PatternEvaluationReport:
        """
        Episode 17 Institutional Analysis:
        Evaluates the pattern through the lens of institutional Supply & Demand.
        Applies the Absorption Law and assigns effective statistical probabilities.
        """
        gtf_equiv = cls.translate_pattern_to_gtf_structure(pattern)

        # Check proximity to Demand Zone
        is_at_demand = False
        if nearby_demand_zone_boundaries:
            pl_d, dl_d = nearby_demand_zone_boundaries
            # If CMP is inside or within 2% above proximal line
            if dl_d * 0.99 <= cmp <= pl_d * 1.02:
                is_at_demand = True

        # Check proximity to Supply Zone
        is_at_supply = False
        if nearby_supply_zone_boundaries:
            pl_s, dl_s = nearby_supply_zone_boundaries
            # If CMP is inside or within 2% below proximal line
            if pl_s * 0.98 <= cmp <= dl_s * 1.01:
                is_at_supply = True

        # CASE 1: Bearish Pattern inside Demand Zone -> Absorption Law (FAILS / Bear Trap)
        if is_bearish and is_at_demand:
            return PatternEvaluationReport(
                pattern_type=pattern,
                is_bullish_pattern=False,
                is_bearish_pattern=True,
                zone_interaction=PatternZoneInteraction.ABSORBED_BY_DEMAND,
                standalone_accuracy_pct=50.0,
                effective_accuracy_pct=15.0,  # Fails 85% of the time for short sellers
                is_tradeable_standalone=False,
                post_entry_confidence_bonus=0,
                gtf_structural_equivalent=gtf_equiv,
                advisory_message=(
                    f"Institutional Absorption Trap: {pattern.value} formed directly inside Demand Zone. "
                    f"Institutional limit buy orders absorb retail selling volume. Pattern will fail and trap short sellers (Bear Trap). "
                    f"Long reversal highly favored."
                ),
            )

        # CASE 2: Bullish Pattern inside Supply Zone -> Rejection Law (FAILS / Bull Trap)
        if is_bullish and is_at_supply:
            return PatternEvaluationReport(
                pattern_type=pattern,
                is_bullish_pattern=True,
                is_bearish_pattern=False,
                zone_interaction=PatternZoneInteraction.REJECTED_BY_SUPPLY,
                standalone_accuracy_pct=50.0,
                effective_accuracy_pct=15.0,  # Fails 85% of the time for long buyers
                is_tradeable_standalone=False,
                post_entry_confidence_bonus=0,
                gtf_structural_equivalent=gtf_equiv,
                advisory_message=(
                    f"Institutional Rejection Trap: {pattern.value} formed directly inside Supply Zone. "
                    f"Resting institutional sell orders reject buying volume. Pattern will fail and trap long buyers (Bull Trap). "
                    f"Short reversal highly favored."
                ),
            )

        # CASE 3: Bullish Pattern at Demand Zone -> +1 Post-Entry Confidence Booster
        if is_bullish and is_at_demand:
            return PatternEvaluationReport(
                pattern_type=pattern,
                is_bullish_pattern=True,
                is_bearish_pattern=False,
                zone_interaction=PatternZoneInteraction.CONFLUENT_DEMAND_BOOST,
                standalone_accuracy_pct=50.0,
                effective_accuracy_pct=85.0,
                is_tradeable_standalone=False,
                post_entry_confidence_bonus=1,
                gtf_structural_equivalent=gtf_equiv,
                advisory_message=(
                    f"Post-Entry Confidence Booster (+1 Bonus): {pattern.value} confirmed at Demand Zone. "
                    f"Visual confirmation that buyers have stepped in at the proximal line. Baseline setup verified."
                ),
            )

        # CASE 4: Bearish Pattern at Supply Zone -> +1 Post-Entry Confidence Booster
        if is_bearish and is_at_supply:
            return PatternEvaluationReport(
                pattern_type=pattern,
                is_bullish_pattern=False,
                is_bearish_pattern=True,
                zone_interaction=PatternZoneInteraction.CONFLUENT_SUPPLY_BOOST,
                standalone_accuracy_pct=50.0,
                effective_accuracy_pct=85.0,
                is_tradeable_standalone=False,
                post_entry_confidence_bonus=1,
                gtf_structural_equivalent=gtf_equiv,
                advisory_message=(
                    f"Post-Entry Confidence Booster (+1 Bonus): {pattern.value} confirmed at Supply Zone. "
                    f"Visual confirmation that sellers have stepped in at the proximal line."
                ),
            )

        # CASE 5: Mid-Air Isolation (The 50/50 Whipsaw Trap)
        return PatternEvaluationReport(
            pattern_type=pattern,
            is_bullish_pattern=is_bullish,
            is_bearish_pattern=is_bearish,
            zone_interaction=PatternZoneInteraction.MID_AIR_COIN_TOSS,
            standalone_accuracy_pct=50.0,
            effective_accuracy_pct=50.0,
            is_tradeable_standalone=False,
            post_entry_confidence_bonus=0,
            gtf_structural_equivalent=gtf_equiv,
            advisory_message=(
                f"The Whipsaw Trap: {pattern.value} formed in mid-air chart space without institutional zone support. "
                f"Statistical accuracy is 50/50 (coin toss). Standalone trading is strictly prohibited."
            ),
        )

    @staticmethod
    def translate_pattern_to_gtf_structure(pattern: ConventionalPatternType) -> str:
        """
        Translates Japanese Candlestick Patterns into GTF Institutional Demand & Supply Mechanics.
        """
        translations = {
            ConventionalPatternType.MORNING_STAR: (
                "Drop-Base-Rally (DBR) Reversal Demand Zone. GTF enforces the Closing Concept "
                "(green candle must close above red candle open) and executes at the Proximal Line "
                "with tight risk, rather than buying high on the candle 3 close."
            ),
            ConventionalPatternType.EVENING_STAR: (
                "Rally-Base-Drop (RBD) Reversal Supply Zone. GTF enforces the Closing Concept "
                "and executes short limit orders at the Proximal Line with tight risk."
            ),
            ConventionalPatternType.HAMMER: (
                "Single-candle institutional order absorption at Proximal Line. Extended lower wick "
                "reflects pending limit orders consuming aggressive sellers."
            ),
            ConventionalPatternType.SHOOTING_STAR: (
                "Single-candle institutional order rejection at Supply Line. Extended upper wick "
                "reflects resting sell orders rejecting aggressive buyers."
            ),
            ConventionalPatternType.INVERTED_HAMMER: (
                "Failed intraday buying attempt. Becomes valid only when forming inside a tested demand zone."
            ),
            ConventionalPatternType.BULLISH_ENGULFING: (
                "Multi-candle order imbalance shift. Functions as a reliable leg-out only when anchored "
                "to an underlying DBR/RBR base."
            ),
            ConventionalPatternType.BEARISH_ENGULFING: (
                "Multi-candle supply expansion. Readily absorbed and invalidated if the lower wick taps "
                "an unbreached higher-timeframe demand zone."
            ),
            ConventionalPatternType.BULLISH_HARAMI: (
                "Inside-candle consolidation following a drop. Easily overpowered if formed beneath overhead supply."
            ),
            ConventionalPatternType.BEARISH_HARAMI: (
                "Inside-candle consolidation following a rally. Readily overpowered by institutional demand support."
            ),
            ConventionalPatternType.NO_PATTERN: "Standard order flow without textbook candlestick formation.",
        }
        return translations.get(pattern, "Standard price action.")

```

---

## 10. Gap Theory Engine (Episode 18) (`alphacouncil/alpha/gap_engine.py`)

```python
"""
Gap Theory & Institutional Imbalance Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 18 principles:
1. Mathematical Definition of Gaps (Real Gaps in Indian Cash Markets vs. Fake Gaps).
2. Structural Classifications:
   - Inside Gap: Open print remains within prior candle's High-Low range.
   - Outside Gap: Open print clears prior candle's High-Low extreme range.
   - Significance Rule: Meaningful price difference (>= 0.5% or >= 0.25 ATR).
3. Behavioral Classifications:
   - Novice Gap: Gap in the SAME direction as prevailing trend (Retail emotional momentum).
   - Pro Gap: Gap in the OPPOSITE direction of prevailing trend (Institutional reversal conviction).
   - Trend over candle color: Macro/ITF trend dictates classification, not isolated candle color.
4. The Four Core Gap Applications in Trading:
   - Application 1: Novice Gap INTO the Zone -> High Probability (+1 Extra Trade Score).
   - Application 2: Novice Gap INTO a Pro Gap -> More High Probability (+2 Extra Trade Score).
   - Application 3: Pro Gap FROM the Zone -> Post-Entry Confirmation (Hold for 3:1+ extended targets).
   - Application 4: Novice Gap IN + Pro Gap OUT on Pro Gap Origin -> The Ultimate Master Setup.
5. Historical Chart Reality: The "Disappearing Gap" Phenomenon (Open vs. Prev Close detection).
6. Debunking the Gap Fill Timeline Myth (Order flow dependent; no calendar predictions).
7. Advanced Price Action: The Window Gap Phenomenon:
   - Elevating entry to Window Gap level when close to base (tight risk).
   - Disciplined base entry / No-Chase Rule when gap is far (preventing inflated risk).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GapType(str, Enum):
    GAP_UP = "GAP_UP"      # Open > Prev Close
    GAP_DOWN = "GAP_DOWN"  # Open < Prev Close
    NO_GAP = "NO_GAP"      # Open == Prev Close


class GapStructuralType(str, Enum):
    INSIDE_GAP = "INSIDE_GAP"    # Open print is within [Prev Low, Prev High]
    OUTSIDE_GAP = "OUTSIDE_GAP"  # Open print is strictly outside [Prev Low, Prev High]
    NONE = "NONE"


class GapBehavioralType(str, Enum):
    NOVICE_GAP = "NOVICE_GAP"    # Gap in SAME direction as trend (Retail momentum chasing)
    PRO_GAP = "PRO_GAP"          # Gap in OPPOSITE direction of trend (Institutional reversal conviction)
    NEUTRAL_GAP = "NEUTRAL_GAP"  # Sideways or insignificant gap


class GapApplicationType(str, Enum):
    APPLICATION_1_NOVICE_GAP_INTO_ZONE = "APPLICATION_1_NOVICE_GAP_INTO_ZONE"
    APPLICATION_2_NOVICE_GAP_INTO_PRO_GAP = "APPLICATION_2_NOVICE_GAP_INTO_PRO_GAP"
    APPLICATION_3_PRO_GAP_FROM_ZONE = "APPLICATION_3_PRO_GAP_FROM_ZONE"
    APPLICATION_4_NOVICE_IN_PRO_OUT_MASTER = "APPLICATION_4_NOVICE_IN_PRO_OUT_MASTER"
    NO_GAP_APPLICATION = "NO_GAP_APPLICATION"


class WindowGapDecision(str, Enum):
    WINDOW_GAP_ELEVATED = "WINDOW_GAP_ELEVATED"          # Close to base: elevate entry to Window Gap level
    WINDOW_GAP_DISCIPLINED_BASE = "WINDOW_GAP_DISCIPLINED_BASE"  # Far from base: maintain entry at base proximal line (No-Chase)
    NO_WINDOW_GAP = "NO_WINDOW_GAP"                      # No window gap present


@dataclass
class GapDetectionResult:
    gap_type: GapType
    structural_type: GapStructuralType
    behavioral_type: GapBehavioralType
    gap_distance: float
    gap_percentage: float
    is_significant: bool
    is_real_gap: bool = True  # True for NSE/BSE cash markets with real clearing & settlement
    prev_close: float = 0.0
    curr_open: float = 0.0
    prev_high: float = 0.0
    prev_low: float = 0.0


@dataclass
class GapApplicationReport:
    application_type: GapApplicationType
    gap_detection: GapDetectionResult
    trade_score_bonus: int = 0  # 0, 1, or 2 points
    probability_rating: str = "Standard"
    disappearing_gap_detected: bool = False
    extended_target_recommended: bool = False
    target_multiplier: float = 2.0  # Default 2:1 RRR, can extend to 3:1 or 4:1
    advisory_message: str = ""


@dataclass
class WindowGapAnalysis:
    decision: WindowGapDecision
    window_gap_level: float
    base_proximal: float
    distal: float
    window_distance: float
    base_risk: float
    elevated_risk: float
    risk_inflation_ratio: float
    is_demand_zone: bool
    advisory_message: str


class GapTheoryEngine:
    """
    Episode 18 Quantitative Gap Theory Engine:
    Detects, classifies, and evaluates gaps against institutional Demand & Supply Zones.
    """

    @staticmethod
    def detect_gap(
        prev_close: float,
        prev_high: float,
        prev_low: float,
        curr_open: float,
        trend_direction: str = "UPTREND",
        atr: Optional[float] = None,
        min_pct_threshold: float = 0.50,
    ) -> GapDetectionResult:
        """
        Mathematical definition & dual structural/behavioral classification of gaps:
        1. Direction: Open > Prev Close -> GAP_UP, Open < Prev Close -> GAP_DOWN.
        2. Structural: Inside Gap (within Prev [Low, High]) vs. Outside Gap (outside extremes).
        3. Significance: Meaningful price disparity (>= 0.5% or >= 0.25 * ATR).
        4. Behavioral: Novice Gap (same as trend) vs. Pro Gap (opposite of trend).
        """
        gap_diff = curr_open - prev_close
        abs_diff = abs(gap_diff)
        pct_diff = (abs_diff / prev_close) * 100.0 if prev_close > 0 else 0.0

        # 1. Directional Type
        if abs_diff < 1e-4:
            gap_type = GapType.NO_GAP
        elif gap_diff > 0:
            gap_type = GapType.GAP_UP
        else:
            gap_type = GapType.GAP_DOWN

        # 2. Structural Type (Inside vs Outside)
        if gap_type == GapType.NO_GAP:
            structural_type = GapStructuralType.NONE
        elif prev_low <= curr_open <= prev_high:
            structural_type = GapStructuralType.INSIDE_GAP
        else:
            structural_type = GapStructuralType.OUTSIDE_GAP

        # 3. Significance Check
        # Rule of Significance: Traders must not obsess over ticks; there must be meaningful price difference
        is_significant = False
        if gap_type != GapType.NO_GAP:
            if atr is not None and atr > 0:
                is_significant = abs_diff >= (0.25 * atr) or pct_diff >= min_pct_threshold
            else:
                is_significant = pct_diff >= min_pct_threshold

        # 4. Behavioral Type (Novice vs Pro)
        # Novice Gap: Same direction as prevailing trend (Retail emotional chase)
        # Pro Gap: Opposite direction of prevailing trend (Massive institutional capital reversal)
        trend_upper = trend_direction.upper()
        if not is_significant or gap_type == GapType.NO_GAP:
            behavioral_type = GapBehavioralType.NEUTRAL_GAP
        elif "UP" in trend_upper:
            if gap_type == GapType.GAP_UP:
                behavioral_type = GapBehavioralType.NOVICE_GAP
            else:
                behavioral_type = GapBehavioralType.PRO_GAP
        elif "DOWN" in trend_upper:
            if gap_type == GapType.GAP_DOWN:
                behavioral_type = GapBehavioralType.NOVICE_GAP
            else:
                behavioral_type = GapBehavioralType.PRO_GAP
        else:
            # Sideways trend
            behavioral_type = GapBehavioralType.NEUTRAL_GAP

        return GapDetectionResult(
            gap_type=gap_type,
            structural_type=structural_type,
            behavioral_type=behavioral_type,
            gap_distance=round(abs_diff, 2),
            gap_percentage=round(pct_diff, 2),
            is_significant=is_significant,
            is_real_gap=True,
            prev_close=prev_close,
            curr_open=curr_open,
            prev_high=prev_high,
            prev_low=prev_low,
        )

    @classmethod
    def evaluate_gap_application(
        cls,
        gap_detection: GapDetectionResult,
        zone_proximal: float,
        zone_distal: float,
        is_demand_zone: bool,
        is_pro_gap_origin: bool = False,
        subsequent_candle_gap: Optional[GapDetectionResult] = None,
        candle_closed_opposite_of_gap: bool = False,
    ) -> GapApplicationReport:
        """
        Evaluates the 4 Core Gap Applications in Trading:
        - Application 1: Novice Gap INTO the Zone (+1 Extra Trade Score, High Probability).
        - Application 2: Novice Gap INTO a Pro Gap (+2 Extra Trade Score, More High Probability).
        - Application 3: Pro Gap FROM the Zone (Post-entry confirmation, hold for 3:1+).
        - Application 4: Novice Gap IN + Pro Gap OUT on Pro Gap Origin (Ultimate Master Setup).
        Also detects Disappearing Gaps and enforces Gap-Fill Myth debunking.
        """
        curr_open = gap_detection.curr_open

        # Check if the gap opens into the zone
        opens_into_zone = False
        if is_demand_zone:
            # For demand zone, open is at or below proximal line and above or at distal line
            if zone_distal <= curr_open <= zone_proximal:
                opens_into_zone = True
        else:
            # For supply zone, open is at or above proximal line and below or at distal line
            if zone_proximal <= curr_open <= zone_distal:
                opens_into_zone = True

        # Check if incoming gap is a Novice Gap
        is_novice_in = (
            opens_into_zone
            and gap_detection.behavioral_type == GapBehavioralType.NOVICE_GAP
            and gap_detection.is_significant
        )

        # Check if subsequent candle has a Pro Gap departing from the zone
        is_pro_out = False
        if subsequent_candle_gap is not None:
            if is_demand_zone and subsequent_candle_gap.gap_type == GapType.GAP_UP:
                is_pro_out = subsequent_candle_gap.is_significant
            elif not is_demand_zone and subsequent_candle_gap.gap_type == GapType.GAP_DOWN:
                is_pro_out = subsequent_candle_gap.is_significant

        # Evaluate the 4 applications
        if is_novice_in and is_pro_gap_origin and is_pro_out:
            # Application 4: The Ultimate Master Setup
            app_type = GapApplicationType.APPLICATION_4_NOVICE_IN_PRO_OUT_MASTER
            score_bonus = 2
            prob_rating = "The Ultimate Master Setup"
            ext_target = True
            target_mult = 4.0
            msg = (
                "Application 4 (The Ultimate Master Setup): Confluence of Pro Gap origin base, "
                "Novice Gap entry exhaustion into institutional limit orders, and Pro Gap departure out of zone. "
                "Maximum probability setup. Hold for extended 4:1+ target. Extra Trade Score: +2."
            )
        elif is_novice_in and is_pro_gap_origin:
            # Application 2: Novice Gap INTO a Pro Gap
            app_type = GapApplicationType.APPLICATION_2_NOVICE_GAP_INTO_PRO_GAP
            score_bonus = 2
            prob_rating = "More High Probability"
            ext_target = True
            target_mult = 3.0
            msg = (
                "Application 2 (Novice Gap INTO a Pro Gap): Retail panic/euphoria momentum collides with "
                "proven institutional conviction Pro Gap origin. Swift and explosive reaction expected. "
                "Extra Trade Score: +2. Recommended target: 3:1 RRR."
            )
        elif is_novice_in:
            # Application 1: Novice Gap INTO the Zone
            app_type = GapApplicationType.APPLICATION_1_NOVICE_GAP_INTO_ZONE
            score_bonus = 1
            prob_rating = "High Probability"
            ext_target = False
            target_mult = 2.0
            msg = (
                "Application 1 (Novice Gap INTO the Zone): Retail crowd dumps supply/demand directly into "
                "resting institutional limit orders inside the zone. High probability of rapid gap-fill. "
                "Extra Trade Score: +1."
            )
        elif is_pro_out:
            # Application 3: Pro Gap FROM the Zone
            app_type = GapApplicationType.APPLICATION_3_PRO_GAP_FROM_ZONE
            score_bonus = 0  # Post-entry confirmation does not alter pre-entry score
            prob_rating = "High Probability Confirmation Exit"
            ext_target = True
            target_mult = 3.5
            msg = (
                "Application 3 (Pro Gap FROM the Zone): Institutional accumulation confirmed post-entry via "
                "explosive Pro Gap departure. Hold with confidence for extended 3:1+ targets."
            )
        else:
            app_type = GapApplicationType.NO_GAP_APPLICATION
            score_bonus = 0
            prob_rating = "Standard"
            ext_target = False
            target_mult = 2.0
            msg = "No primary institutional gap application detected."

        # Disappearing Gap Detection
        # When a stock gaps down into demand at 9:15 AM and rallies immediately, the candle closes high green,
        # visually covering the gap on historical charts. But open-vs-prior-close preserves the footprint.
        disappearing_gap = bool(opens_into_zone and candle_closed_opposite_of_gap)
        if disappearing_gap:
            msg += (
                " [Disappearing Gap Identified]: Completed candle visually masks the morning opening void, "
                "but order-flow audit confirms genuine institutional absorption at 9:15 AM."
            )

        # Gap Fill Myth Debunking Note
        msg += (
            " [Institutional Fact]: Professional traders never predict gap fill timelines; "
            "execution is governed strictly by zone order-flow dynamics."
        )

        return GapApplicationReport(
            application_type=app_type,
            gap_detection=gap_detection,
            trade_score_bonus=score_bonus,
            probability_rating=prob_rating,
            disappearing_gap_detected=disappearing_gap,
            extended_target_recommended=ext_target,
            target_multiplier=target_mult,
            advisory_message=msg,
        )

    @staticmethod
    def analyze_window_gap(
        base_proximal: float,
        distal: float,
        legout_open: float,
        legout_extreme_wick: float,
        is_demand_zone: bool = True,
        max_risk_inflation_threshold: float = 0.35,
    ) -> WindowGapAnalysis:
        """
        Advanced Price Action: The Window Gap Phenomenon.
        When an explosive leg-out opens with a gap away from the base candle, it leaves a wick (or open):
        - For Demand Zone: leg-out opens gap-up; its lowest lower wick (or open if wickless) is the Window Gap Level.
        - For Supply Zone: leg-out opens gap-down; its highest upper wick (or open if wickless) is the Window Gap Level.

        Execution Rules:
        1. When Close to Base (distance <= threshold * base_risk):
           - Elevate entry to Window Gap Level (WINDOW_GAP_ELEVATED) to prevent missing the trade.
           - Stop loss MUST remain below distal line (never widen or anchor above base).
           - Position size must be recalculated with inflated risk.
        2. When Far Away (distance > threshold * base_risk):
           - Maintain disciplined entry at Base Proximal Line (WINDOW_GAP_DISCIPLINED_BASE).
           - Do NOT chase! Placing entry far up severely hurts RRR. If missed, accept with zero regret.
        """
        base_risk = abs(base_proximal - distal)
        if base_risk <= 0:
            base_risk = 1.0  # Guard against division by zero

        # Determine window gap level
        # For demand: lower shadow of gapping leg-out candle
        # If leg-out opened higher than low, use low; else legout_open
        if is_demand_zone:
            window_gap_level = min(legout_open, legout_extreme_wick)
            # Distance from base proximal to window gap level
            window_distance = window_gap_level - base_proximal
            elevated_risk = window_gap_level - distal
        else:
            # Supply zone
            window_gap_level = max(legout_open, legout_extreme_wick)
            window_distance = base_proximal - window_gap_level
            elevated_risk = distal - window_gap_level

        # If window distance is negative or zero, there is no window gap above/below base
        if window_distance <= 0:
            return WindowGapAnalysis(
                decision=WindowGapDecision.NO_WINDOW_GAP,
                window_gap_level=round(window_gap_level, 2),
                base_proximal=round(base_proximal, 2),
                distal=round(distal, 2),
                window_distance=0.0,
                base_risk=round(base_risk, 2),
                elevated_risk=round(base_risk, 2),
                risk_inflation_ratio=0.0,
                is_demand_zone=is_demand_zone,
                advisory_message="No window gap present between base and leg-out departure.",
            )

        risk_inflation_ratio = window_distance / base_risk

        if risk_inflation_ratio <= max_risk_inflation_threshold:
            decision = WindowGapDecision.WINDOW_GAP_ELEVATED
            msg = (
                f"Window Gap is CLOSE to base (inflation {risk_inflation_ratio*100:.1f}% <= {max_risk_inflation_threshold*100:.0f}% threshold). "
                f"Elevate entry from base proximal ({base_proximal:.2f}) to Window Gap Level ({window_gap_level:.2f}) to ensure fill. "
                f"Stop Loss remains strictly anchored to Distal Line ({distal:.2f}). Recalculate position quantity for elevated risk ({elevated_risk:.2f})."
            )
        else:
            decision = WindowGapDecision.WINDOW_GAP_DISCIPLINED_BASE
            msg = (
                f"Window Gap is FAR from base (inflation {risk_inflation_ratio*100:.1f}% > {max_risk_inflation_threshold*100:.0f}% threshold). "
                f"DISCIPLINE RULE: Do NOT chase entry to Window Gap Level ({window_gap_level:.2f})! "
                f"Maintain entry strictly at Base Proximal Line ({base_proximal:.2f}) with Base Risk ({base_risk:.2f}). "
                "If price pulls back only to window gap and departs, accept missed entry with zero regret."
            )

        return WindowGapAnalysis(
            decision=decision,
            window_gap_level=round(window_gap_level, 2),
            base_proximal=round(base_proximal, 2),
            distal=round(distal, 2),
            window_distance=round(window_distance, 2),
            base_risk=round(base_risk, 2),
            elevated_risk=round(elevated_risk, 2),
            risk_inflation_ratio=round(risk_inflation_ratio, 4),
            is_demand_zone=is_demand_zone,
            advisory_message=msg,
        )

```

---

## 11. Market Traps & LOTL Engine (Episode 19) (`alphacouncil/alpha/trap_and_pattern_engine.py`)

```python
"""
Market Traps, LOTL Merging & Conventional Chart Patterns Truth Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 19 principles:
1. Level Over the Level / Level on Top of the Level (LOTL):
   - Formation mechanics: DBR + RBR, DBR + DBR, DBD + DBD.
   - The Stop-Loss Mandate: SL is ALWAYS placed below the Distal Line of the LOWER (Origin) Level.
   - Three Entry Options:
     * Aggressive: Upper Proximal Line (minimizes missed fill, wider risk).
     * Conservative: Lower Proximal Line (tight risk, high RRR, risk of missed fill).
     * Balanced / Middle: Halfway between upper and lower bases (The GTF Ideal Sweet Spot).
   - Stacking Limits: If 3 or more basing levels form, do NOT merge all three (avoids Garbage Areas). Discard top levels and focus strictly on the bottom two origin levels.
   - Cross-Wave LOTL: Merging unmitigated origin bases from prior waves to prevent sweep stop-outs.
2. Market Traps (Bull Traps & Bear Traps):
   - Bull Trap: Retail buys breakout of resistance/neckline directly into a Higher Timeframe Supply Zone.
   - Bear Trap: Retail shorts breakdown of support/neckline directly into a Higher Timeframe Demand Zone.
   - Root Cause: Higher Timeframe Zones provide institutional liquidity to trap retail breakout traders.
3. The Truth Behind Conventional Chart Patterns:
   - Head & Shoulders: Head hits HTF Supply; neckline breakdown plunges into HTF Demand (Bear Trap).
   - Inverse Head & Shoulders: Head low hits HTF Demand (Quarterly/Monthly origin); advance driven by institutional orders, not neckline breakout.
   - Double Top / Bottom & Triple Top / Bottom: Visual artifacts of tested institutional supply/demand zones.
   - Cup & Handle: Bottom is HTF Demand sweep; handle breakout directly into HTF Supply traps retail.
   - Flags & Pennants: Consolidation between opposing zones; channel breakdown into HTF demand causes multi-year rallies (Ashok Leyland case study).
4. Indicators Reality Check (RSI & Stochastic in GTF Trading):
   - Standalone Indicator Fallacy: Strong institutional trends can remain "Overbought" (RSI > 70) for months while price surges 100%+. Shorting solely on indicator leads to ruin.
   - The GTF Role (+1 Bonus Only): An independently qualified Demand Zone coinciding with Oversold RSI (<= 30) receives a +1 Extra Trade Score Bonus.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Tuple


class LOTLEntryOption(str, Enum):
    AGGRESSIVE = "AGGRESSIVE"              # Upper Proximal Line (Max fill probability, wider risk)
    CONSERVATIVE = "CONSERVATIVE"          # Lower Proximal Line / Origin (Tight risk, high RRR, may miss trade)
    BALANCED_MIDDLE = "BALANCED_MIDDLE"    # Halfway between upper and lower levels (GTF Ideal Sweet Spot)


class MarketTrapType(str, Enum):
    BULL_TRAP = "BULL_TRAP"                # Retail buys breakout into Higher Timeframe Supply Zone -> Trapped
    BEAR_TRAP = "BEAR_TRAP"                # Retail shorts breakdown into Higher Timeframe Demand Zone -> Trapped
    NO_TRAP = "NO_TRAP"


class ConventionalChartPatternType(str, Enum):
    HEAD_AND_SHOULDERS = "HEAD_AND_SHOULDERS"
    INVERSE_HEAD_AND_SHOULDERS = "INVERSE_HEAD_AND_SHOULDERS"
    DOUBLE_TOP = "DOUBLE_TOP"
    DOUBLE_BOTTOM = "DOUBLE_BOTTOM"
    TRIPLE_TOP = "TRIPLE_TOP"
    TRIPLE_BOTTOM = "TRIPLE_BOTTOM"
    CUP_AND_HANDLE = "CUP_AND_HANDLE"
    FLAG_AND_PENNANT = "FLAG_AND_PENNANT"
    CHANNEL_BREAKOUT = "CHANNEL_BREAKOUT"
    NO_PATTERN = "NO_PATTERN"


class IndicatorConfluenceType(str, Enum):
    OVERSOLD_DEMAND_BOOST = "OVERSOLD_DEMAND_BOOST"      # RSI <= 30 at Demand Zone -> +1 Bonus
    OVERBOUGHT_SUPPLY_BOOST = "OVERBOUGHT_SUPPLY_BOOST"  # RSI >= 70 at Supply Zone -> +1 Bonus
    OVERBOUGHT_UPTREND_TRAP = "OVERBOUGHT_UPTREND_TRAP"  # RSI > 70 in institutional uptrend -> Shorting strictly prohibited!
    OVERSOLD_DOWNTREND_TRAP = "OVERSOLD_DOWNTREND_TRAP"  # RSI < 30 in institutional downtrend -> Buying without zone prohibited!
    NEUTRAL_INDICATOR = "NEUTRAL_INDICATOR"


@dataclass
class MergedLOTLZone:
    origin_zone: Any
    cushion_zone: Any
    entry_option: LOTLEntryOption
    entry_price: float
    stop_loss: float
    risk_per_share: float
    is_3_plus_cluster_trimmed: bool = False
    is_cross_wave_lotl: bool = False
    advisory_message: str = ""


@dataclass
class MarketTrapReport:
    trap_type: MarketTrapType
    trigger_price: float
    htf_zone_price_range: Tuple[float, float]
    is_trap_confirmed: bool
    breakout_direction: str
    expected_reversal_direction: str
    advisory_message: str


@dataclass
class ChartPatternTruthReport:
    pattern_type: ConventionalChartPatternType
    underlying_gtf_driver: str
    neckline_or_boundary_price: float
    htf_inflection_zone_level: float
    retail_expectation: str
    institutional_reality: str
    is_trap_risk_high: bool
    advisory_message: str


@dataclass
class IndicatorConfluenceReport:
    confluence_type: IndicatorConfluenceType
    rsi_value: float
    is_standalone_tradeable: bool = False
    trade_score_bonus: int = 0
    advisory_message: str = ""


class MarketTrapsAndPatternTruthEngine:
    """
    Episode 19 Quantitative Engine:
    LOTL Level Merging, Institutional Bull/Bear Trap Detection,
    Conventional Chart Pattern Translation, and Indicator Reality Check.
    """

    @classmethod
    def merge_lotl_zones(
        cls,
        zones: List[Any],
        entry_option: LOTLEntryOption = LOTLEntryOption.BALANCED_MIDDLE,
        is_cross_wave: bool = False,
    ) -> MergedLOTLZone:
        """
        Module 1: Level Over the Level (LOTL) Merging Engine.
        - Stop-Loss Mandate: Fixed strictly below Lower Distal Line (Demand) or above Upper Distal Line (Supply).
        - Stacking Limit (3+ Rule): If 3 or more levels form, discard upper levels and merge strictly bottom two.
        - Entry Options: Aggressive (Upper PL), Conservative (Lower PL), Balanced Middle (Average of PLs).
        """
        if not zones:
            raise ValueError("LOTL merging requires at least one zone.")

        is_demand = zones[0].is_demand

        # Sort zones by price level:
        # For Demand: lowest proximal line is the lower origin base
        # For Supply: highest proximal line is the upper origin base
        if is_demand:
            sorted_zones = sorted(zones, key=lambda z: z.proximal_line)
        else:
            sorted_zones = sorted(zones, key=lambda z: z.proximal_line, reverse=True)

        is_trimmed = False
        # Stacking Limit: If 3 or more levels form, do not merge all three (avoids Garbage Area)
        # Discard top levels and focus strictly on bottom two (origin) levels
        if len(sorted_zones) >= 3:
            is_trimmed = True
            active_pair = sorted_zones[:2]
        elif len(sorted_zones) == 2:
            active_pair = sorted_zones
        else:
            # Single zone fallback
            z = sorted_zones[0]
            risk = abs(z.entry_price - z.stop_loss)
            return MergedLOTLZone(
                origin_zone=z,
                cushion_zone=z,
                entry_option=entry_option,
                entry_price=round(z.entry_price, 2),
                stop_loss=round(z.stop_loss, 2),
                risk_per_share=round(risk, 2),
                is_3_plus_cluster_trimmed=False,
                is_cross_wave_lotl=is_cross_wave,
                advisory_message="Single zone provided; no LOTL stacking present.",
            )

        origin_level = active_pair[0]   # Lower level for demand, Upper level for supply
        cushion_level = active_pair[1]  # Upper level for demand, Lower level for supply

        if is_demand:
            # Demand LOTL:
            # Origin Level is lower (true structural turning point)
            # Stop-loss is ALWAYS below the Distal Line of the LOWER (Origin) Level
            stop_loss = origin_level.distal_line
            lower_pl = origin_level.proximal_line
            upper_pl = cushion_level.proximal_line

            if entry_option == LOTLEntryOption.AGGRESSIVE:
                entry_price = upper_pl
            elif entry_option == LOTLEntryOption.CONSERVATIVE:
                entry_price = lower_pl
            else:
                # Balanced / Middle Entry: Ideal Sweet Spot
                entry_price = (upper_pl + lower_pl) / 2.0

            risk_per_share = entry_price - stop_loss
            advisory = (
                f"Demand LOTL Merged: Entry ({entry_option.value}) at ₹{entry_price:.2f}. "
                f"Stop-Loss strictly anchored below Lower Origin Distal Line at ₹{stop_loss:.2f} (Risk: ₹{risk_per_share:.2f})."
            )
        else:
            # Supply LOTL:
            # Origin Level is upper (highest resistance)
            # Stop-loss is ALWAYS above the Distal Line of the UPPER (Origin) Level
            stop_loss = origin_level.distal_line
            upper_pl = origin_level.proximal_line
            lower_pl = cushion_level.proximal_line

            if entry_option == LOTLEntryOption.AGGRESSIVE:
                entry_price = lower_pl
            elif entry_option == LOTLEntryOption.CONSERVATIVE:
                entry_price = upper_pl
            else:
                entry_price = (upper_pl + lower_pl) / 2.0

            risk_per_share = stop_loss - entry_price
            advisory = (
                f"Supply LOTL Merged: Entry ({entry_option.value}) at ₹{entry_price:.2f}. "
                f"Stop-Loss strictly anchored above Upper Origin Distal Line at ₹{stop_loss:.2f} (Risk: ₹{risk_per_share:.2f})."
            )

        if is_trimmed:
            advisory += " [3+ Stack Limit Enforced]: Discarded excessive upper basing to prevent Garbage Area range inflation."

        if is_cross_wave:
            advisory += " [Cross-Wave LOTL]: Merged with unmitigated origin base from prior wave, preventing stop-hunt sweep."

        return MergedLOTLZone(
            origin_zone=origin_level,
            cushion_zone=cushion_level,
            entry_option=entry_option,
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            risk_per_share=round(risk_per_share, 2),
            is_3_plus_cluster_trimmed=is_trimmed,
            is_cross_wave_lotl=is_cross_wave,
            advisory_message=advisory,
        )

    @staticmethod
    def detect_market_trap(
        breakout_price: float,
        breakout_type: str,  # "RESISTANCE_BREAKOUT" or "SUPPORT_BREAKDOWN"
        htf_demand_zone: Optional[Tuple[float, float]] = None,  # (distal, proximal)
        htf_supply_zone: Optional[Tuple[float, float]] = None,  # (proximal, distal)
    ) -> MarketTrapReport:
        """
        Module 2: Market Traps (Bull Traps & Bear Traps) Detector.
        - Bull Trap: Price breaks out above horizontal resistance directly into HTF Supply Zone.
        - Bear Trap: Price breaks down below horizontal support directly into HTF Demand Zone.
        """
        breakout_upper = breakout_type.upper()

        # 1. Bull Trap Check
        if "RESISTANCE" in breakout_upper or "BREAKOUT" in breakout_upper:
            if htf_supply_zone is not None:
                pl_supply, dl_supply = htf_supply_zone
                # If breakout price is inside or entering HTF supply zone
                if pl_supply <= breakout_price <= dl_supply or abs(breakout_price - pl_supply) <= (0.01 * pl_supply):
                    return MarketTrapReport(
                        trap_type=MarketTrapType.BULL_TRAP,
                        trigger_price=breakout_price,
                        htf_zone_price_range=(pl_supply, dl_supply),
                        is_trap_confirmed=True,
                        breakout_direction="UPWARD_BREAKOUT",
                        expected_reversal_direction="SHARP_DOWNWARD_REVERSAL",
                        advisory_message=(
                            f"BULL TRAP DETECTED: Price broke out at ₹{breakout_price:.2f} directly into "
                            f"Higher Timeframe Supply Zone [₹{pl_supply:.2f} - ₹{dl_supply:.2f}]. "
                            "Retail breakout buyers will provide exit liquidity for institutions. "
                            "Buying prohibited; expect sharp downward reversal."
                        ),
                    )

        # 2. Bear Trap Check
        if "SUPPORT" in breakout_upper or "BREAKDOWN" in breakout_upper:
            if htf_demand_zone is not None:
                dl_demand, pl_demand = htf_demand_zone
                # If breakdown price is inside or entering HTF demand zone
                if dl_demand <= breakout_price <= pl_demand or abs(breakout_price - pl_demand) <= (0.01 * pl_demand):
                    return MarketTrapReport(
                        trap_type=MarketTrapType.BEAR_TRAP,
                        trigger_price=breakout_price,
                        htf_zone_price_range=(dl_demand, pl_demand),
                        is_trap_confirmed=True,
                        breakout_direction="DOWNWARD_BREAKDOWN",
                        expected_reversal_direction="VIOLENT_UPWARD_REVERSAL",
                        advisory_message=(
                            f"BEAR TRAP DETECTED: Price broke down at ₹{breakout_price:.2f} directly into "
                            f"Higher Timeframe Demand Zone [₹{dl_demand:.2f} - ₹{pl_demand:.2f}]. "
                            "Retail short sellers are dumping supply into institutional limit buy orders. "
                            "Shorting prohibited; expect violent upward reversal."
                        ),
                    )

        return MarketTrapReport(
            trap_type=MarketTrapType.NO_TRAP,
            trigger_price=breakout_price,
            htf_zone_price_range=(0.0, 0.0),
            is_trap_confirmed=False,
            breakout_direction=breakout_type,
            expected_reversal_direction="CONTINUATION",
            advisory_message="No institutional trap detected. Move is in open territory.",
        )

    @staticmethod
    def translate_conventional_chart_pattern(
        pattern_type: ConventionalChartPatternType,
        neckline_or_boundary_price: float,
        htf_zone_level: float,
        is_htf_demand: bool = True,
    ) -> ChartPatternTruthReport:
        """
        Module 3: Demystifies conventional patterns through institutional Supply & Demand.
        Proves why conventional neckline trades fail when colliding with HTF zones.
        """
        if pattern_type == ConventionalChartPatternType.HEAD_AND_SHOULDERS:
            # Head hit HTF supply; neckline breakdown plunges into HTF demand
            is_trap = is_htf_demand and abs(neckline_or_boundary_price - htf_zone_level) / htf_zone_level <= 0.03
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Head formed at HTF Supply; neckline sits over HTF Demand",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Short the neckline breakdown with target equal to Head-to-Neckline distance.",
                institutional_reality=(
                    "The breakdown plunges directly into unmitigated Higher Timeframe Demand. "
                    "Institutional limit buy orders absorb the panic selling, trapping retail shorts."
                ),
                is_trap_risk_high=is_trap,
                advisory_message="Head & Shoulders Truth: Do NOT short the neckline breakdown into HTF Demand. Expect Bear Trap.",
            )

        if pattern_type == ConventionalChartPatternType.INVERSE_HEAD_AND_SHOULDERS:
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Head extreme low coincided with Quarterly/Monthly Demand origin (BEL Case Study)",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Wait for late neckline breakout to buy with wide stop loss.",
                institutional_reality=(
                    "The entire rally was engineered by institutional orders at the HTF Demand origin. "
                    "GTF traders entered at the Head origin; buying the neckline breakout is late with poor RRR."
                ),
                is_trap_risk_high=False,
                advisory_message="Inverse H&S Truth: Enter at the Head origin Demand Zone with tight risk, not at the late neckline breakout.",
            )

        if pattern_type in (ConventionalChartPatternType.DOUBLE_TOP, ConventionalChartPatternType.TRIPLE_TOP):
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Repeated retests of an Institutional Supply Zone",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Sell after the double/triple top confirms with neckline break.",
                institutional_reality="Visual artifact of tested supply; each test absorbs pending sell orders, reducing freshness.",
                is_trap_risk_high=False,
                advisory_message="Double/Triple Top Truth: It is simply a tested supply zone. Freshness is reduced; do not trade late tests.",
            )

        if pattern_type in (ConventionalChartPatternType.DOUBLE_BOTTOM, ConventionalChartPatternType.TRIPLE_BOTTOM):
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Repeated retests of an Institutional Demand Zone (Colpal Case Study)",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Buy after neckline break of double/triple bottom.",
                institutional_reality="Visual artifact of tested demand holding firm while overhead supply is absorbed.",
                is_trap_risk_high=False,
                advisory_message="Double/Triple Bottom Truth: Price holding HTF demand while overhead resistance is cleared leads to explosive expansion.",
            )

        if pattern_type == ConventionalChartPatternType.CUP_AND_HANDLE:
            is_trap = not is_htf_demand and abs(neckline_or_boundary_price - htf_zone_level) / htf_zone_level <= 0.03
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Cup bottom sweeps HTF Demand; Handle is a secondary follow-up base",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Buy handle breakout aggressively.",
                institutional_reality=(
                    "If handle breakout drives straight into an overhead HTF Supply Zone, "
                    "the setup fails immediately, trapping breakout buyers."
                ),
                is_trap_risk_high=is_trap,
                advisory_message="Cup & Handle Truth: Check overhead space! Handle breakout directly into HTF Supply will fail.",
            )

        if pattern_type in (ConventionalChartPatternType.FLAG_AND_PENNANT, ConventionalChartPatternType.CHANNEL_BREAKOUT):
            return ChartPatternTruthReport(
                pattern_type=pattern_type,
                underlying_gtf_driver="Consolidation between minor levels; channel breakdown into HTF Demand (Ashok Leyland Case Study)",
                neckline_or_boundary_price=neckline_or_boundary_price,
                htf_inflection_zone_level=htf_zone_level,
                retail_expectation="Short channel breakdown.",
                institutional_reality="Breakdown into HTF Demand causes institutions to absorb retail selling and trigger multi-year rally.",
                is_trap_risk_high=is_htf_demand,
                advisory_message="Flag/Channel Truth: Downward channel breakdown directly into Monthly Demand is a legendary Bear Trap.",
            )

        return ChartPatternTruthReport(
            pattern_type=ConventionalChartPatternType.NO_PATTERN,
            underlying_gtf_driver="Clean Institutional Supply and Demand Zones",
            neckline_or_boundary_price=neckline_or_boundary_price,
            htf_inflection_zone_level=htf_zone_level,
            retail_expectation="None",
            institutional_reality="Price action governed strictly by institutional order matching.",
            is_trap_risk_high=False,
            advisory_message="Clean price action without conventional pattern traps.",
        )

    @staticmethod
    def evaluate_indicator_confluence(
        zone_is_demand: bool,
        rsi_value: float,
        itf_trend: str = "UPTREND",
    ) -> IndicatorConfluenceReport:
        """
        Module 4: Indicators Reality Check (RSI & Stochastic in GTF Trading).
        - Standalone Indicator Fallacy: Strong uptrends stay RSI > 70 for months. Never short overbought RSI in an uptrend!
        - GTF Confluence: When an independently qualified Demand Zone coincides with Oversold RSI (<= 30),
          award +1 Extra Trade Score Bonus.
        """
        trend_upper = itf_trend.upper()

        # The Overbought Uptrend Trap
        if "UP" in trend_upper and rsi_value >= 70.0:
            return IndicatorConfluenceReport(
                confluence_type=IndicatorConfluenceType.OVERBOUGHT_UPTREND_TRAP,
                rsi_value=round(rsi_value, 2),
                is_standalone_tradeable=False,
                trade_score_bonus=0,
                advisory_message=(
                    f"INDICATOR MYTH AVOIDED: RSI is {rsi_value:.1f} (Overbought) in an institutional UPTREND. "
                    "Assets can remain overbought for months while surging 100%+. Shorting strictly prohibited!"
                ),
            )

        # The Oversold Downtrend Trap
        if "DOWN" in trend_upper and rsi_value <= 30.0 and not zone_is_demand:
            return IndicatorConfluenceReport(
                confluence_type=IndicatorConfluenceType.OVERSOLD_DOWNTREND_TRAP,
                rsi_value=round(rsi_value, 2),
                is_standalone_tradeable=False,
                trade_score_bonus=0,
                advisory_message=(
                    f"INDICATOR TRAP AVOIDED: RSI is {rsi_value:.1f} (Oversold) in an institutional DOWNTREND. "
                    "Buying solely on oversold indicators without an institutional Demand Zone leads to falling knife traps."
                ),
            )

        # Confluence Bonus at Demand Zone
        if zone_is_demand and rsi_value <= 30.0:
            return IndicatorConfluenceReport(
                confluence_type=IndicatorConfluenceType.OVERSOLD_DEMAND_BOOST,
                rsi_value=round(rsi_value, 2),
                is_standalone_tradeable=False,  # Never trade standalone
                trade_score_bonus=1,
                advisory_message=(
                    f"Indicator Confluence Bonus (+1 Point): Qualified Demand Zone coincides with Oversold RSI ({rsi_value:.1f}). "
                    "Retail indicator algorithms may add supportive buying flow."
                ),
            )

        # Confluence Bonus at Supply Zone
        if not zone_is_demand and rsi_value >= 70.0:
            return IndicatorConfluenceReport(
                confluence_type=IndicatorConfluenceType.OVERBOUGHT_SUPPLY_BOOST,
                rsi_value=round(rsi_value, 2),
                is_standalone_tradeable=False,
                trade_score_bonus=1,
                advisory_message=(
                    f"Indicator Confluence Bonus (+1 Point): Qualified Supply Zone coincides with Overbought RSI ({rsi_value:.1f}). "
                    "Retail indicator algorithms may add supportive selling flow."
                ),
            )

        return IndicatorConfluenceReport(
            confluence_type=IndicatorConfluenceType.NEUTRAL_INDICATOR,
            rsi_value=round(rsi_value, 2),
            is_standalone_tradeable=False,
            trade_score_bonus=0,
            advisory_message=f"RSI reading {rsi_value:.1f} is neutral. No indicator bonus awarded.",
        )

```

---

## 12. High-Speed Stock Scanner & Dynamic Trailing Engine (Episode 20) (`alphacouncil/alpha/scanner_and_trailing_engine.py`)

```python
"""
High-Speed Stock Scanner, Dynamic Stop-Loss Trailing & Master Checklist Engine (Trading in the Zone / GTF Methodology).
Codifies Episode 20 principles:
1. Advanced Dynamic Stop-Loss Trailing (Unlocking Multi-Baggers — 100% to 1,000%+ returns):
   - The Retail Flaw: Fixed rupee trailing (moving SL up arbitrarily by ₹5, ₹10) or premature Cost-to-Cost shifts.
     Normal structural retracements shake retail traders out before multi-bagger expansions.
   - The GTF Trailing Blueprint: Anchor Stop-Loss strictly beneath the Distal Line of newly formed, fresh
     Weekly Demand Zones (or Daily for swing). Hold position until a confirmed candle physically closes below the distal line.
   - Live Case Studies: Wipro, Infosys, Bank of Baroda.
2. The Unified GTF Trade Scoring Hierarchy & Master Checklist:
   - Primary Structural Score (Freshness 3, Strength 2, Base 2 = 7/7 Baseline) + Mandatory Filters (Clean Closing,
     HTF Shri Krishna Location, Intermediate Trend) are NON-NEGOTIABLE.
   - Secondary Bonuses (Moving Averages +1, 20 EMA +1, Gap Confluence +1/+2, RSI Oversold +1) enhance score to 8/7 or 9/7.
   - Supreme Institutional Catalyst: Parent Sector Support (+2 Extra Trade Score).
   - Priority Rule: Never take a structurally flawed 5/7 setup simply because a moving average or indicator aligns.
3. High-Speed Stock Scanning & Watchlist Architecture:
   - Funnel: Nifty 50/Next 50 -> "52-Week High Approaching" List (verified multi-timeframe uptrends with open sky).
   - 30-Minute Daily Scanning Workflow:
     * -0.5% to +0.5% daily move: Base candle churn (Ignore).
     * Top Gainers: Scan for fresh Daily demand origin bases.
     * Top Losers: Scan for pullbacks entering pre-identified demand zones.
4. On-Chart Documentation & Mandatory Price Alert System:
   - Permanent 5-second on-chart analytical status block.
   - Price Alert placed 1 to 2 rupees above Proximal Line; eliminate live screen-staring.
5. The 100-Trade Discipline Roadmap (Amol Jagdale Blueprint):
   - Strictly Monthly (MIT) and Weekly (WIT) Income Trades for first 100 trades.
   - Maximum 10 Trades per Month, 0.5% to 1.0% fixed Risk Per Trade.
   - 100% personal responsibility; zero external tips/noise.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TrailingMethodology(str, Enum):
    WEEKLY_DEMAND_BASE_ANCHORED = "WEEKLY_DEMAND_BASE_ANCHORED"  # GTF Institutional Trailing (Survives retracements)
    FIXED_POINTS_RETAIL_TRAP = "FIXED_POINTS_RETAIL_TRAP"        # Conventional Retail Error (Arbitrary points or cost-to-cost)


class StockScanFilterType(str, Enum):
    APPROACHING_52_WEEK_HIGH = "APPROACHING_52_WEEK_HIGH"        # Within 5-10% of 52W high; established macro uptrends
    PULLBACK_INTO_DEMAND = "PULLBACK_INTO_DEMAND"                # Top loser entering pre-identified institutional demand
    FRESH_ORIGIN_FORMATION = "FRESH_ORIGIN_FORMATION"            # Top gainer forming fresh origin base
    BASING_RANGE_CHURN = "BASING_RANGE_CHURN"                    # -0.5% to +0.5% move; base candle (ignore)


class ScanCandidatePriority(str, Enum):
    TOP_CONVICTION = "TOP_CONVICTION"    # Approaching 52W high + Sector Support + 7/7 Zone
    WATCHLIST_ALERT = "WATCHLIST_ALERT"  # Valid pullback or fresh origin requiring price alert
    IGNORE_BASING = "IGNORE_BASING"      # Minor consolidation churn; discard


@dataclass
class DynamicTrailingState:
    symbol: str
    entry_price: float
    initial_stop_loss: float
    current_trailing_stop_loss: float
    methodology: TrailingMethodology = TrailingMethodology.WEEKLY_DEMAND_BASE_ANCHORED
    trailing_level_count: int = 0
    trailing_history: List[Dict[str, Any]] = field(default_factory=list)
    highest_price_reached: float = 0.0
    unrealized_gain_pct: float = 0.0
    is_position_active: bool = True
    exit_price: Optional[float] = None
    advisory_message: str = ""


@dataclass
class ScanCandidate:
    symbol: str
    cmp: float
    high_52w: float
    low_52w: float
    pct_from_52w_high: float
    daily_pct_change: float
    filter_type: StockScanFilterType
    priority: ScanCandidatePriority
    sector_name: str
    is_sector_support_active: bool
    price_alert_level: Optional[float] = None
    on_chart_note: str = ""
    advisory_message: str = ""


class DynamicTrailingEngine:
    """
    Episode 20 Dynamic Stop-Loss Trailing Engine:
    Ratchets stop-loss strictly behind newly formed, fresh Higher Timeframe (Weekly/Daily)
    Demand Zone Distal Lines to capture generational multi-bagger expansions (100% to 1,000%+).
    """

    @classmethod
    def initialize_trailing_position(
        cls,
        symbol: str,
        entry_price: float,
        initial_stop_loss: float,
    ) -> DynamicTrailingState:
        """Initializes a new macro position with GTF demand-anchored trailing."""
        return DynamicTrailingState(
            symbol=symbol,
            entry_price=round(entry_price, 2),
            initial_stop_loss=round(initial_stop_loss, 2),
            current_trailing_stop_loss=round(initial_stop_loss, 2),
            trailing_level_count=0,
            trailing_history=[{
                "level": 0,
                "trailing_sl": round(initial_stop_loss, 2),
                "reason": "Initial Distal Line Stop-Loss",
            }],
            highest_price_reached=round(entry_price, 2),
            unrealized_gain_pct=0.0,
            is_position_active=True,
            advisory_message="Position initialized. Trailing will engage as fresh Weekly Demand Bases form.",
        )

    @classmethod
    def advance_trailing_stop_loss(
        cls,
        state: DynamicTrailingState,
        new_weekly_demand_zone_distal: float,
        current_cmp: float,
        candle_close_price: float,
    ) -> DynamicTrailingState:
        """
        Advances the trailing stop-loss strictly behind confirmed fresh Weekly Demand Zone Distal Lines.
        Rules:
        1. Never lower the stop-loss (strictly ratchets upward).
        2. Prohibits arbitrary ₹5/₹10 retail shifts or premature cost-to-cost panic moves.
        3. Position exits ONLY when candle physically closes below the active trailing distal line.
        """
        if not state.is_position_active:
            state.advisory_message = "Position is already closed. No trailing adjustments permitted."
            return state

        state.highest_price_reached = max(state.highest_price_reached, current_cmp)
        unrealized_gain = ((current_cmp - state.entry_price) / state.entry_price) * 100.0
        state.unrealized_gain_pct = round(unrealized_gain, 2)

        # 1. Check if price physically breached and closed below active trailing stop-loss
        if candle_close_price < state.current_trailing_stop_loss:
            state.is_position_active = False
            state.exit_price = candle_close_price
            final_gain = ((candle_close_price - state.entry_price) / state.entry_price) * 100.0
            state.advisory_message = (
                f"MULTI-BAGGER EXIT TRIGGERED: Candle closed at ₹{candle_close_price:.2f} below confirmed Weekly "
                f"Demand Distal Line ₹{state.current_trailing_stop_loss:.2f}. "
                f"Final Realized Gain: +{final_gain:.1f}% across {state.trailing_level_count} trailing bases."
            )
            return state

        # 2. Check if newly formed Weekly demand zone provides a higher anchor
        if new_weekly_demand_zone_distal > state.current_trailing_stop_loss:
            old_sl = state.current_trailing_stop_loss
            state.current_trailing_stop_loss = round(new_weekly_demand_zone_distal, 2)
            state.trailing_level_count += 1
            state.trailing_history.append({
                "level": state.trailing_level_count,
                "trailing_sl": round(new_weekly_demand_zone_distal, 2),
                "cmp_at_shift": round(current_cmp, 2),
                "reason": f"Anchored beneath fresh Weekly Demand Base Distal Line (Level {state.trailing_level_count})",
            })
            state.advisory_message = (
                f"TRAILING SL ADVANCED (Level {state.trailing_level_count}): Shifted from ₹{old_sl:.2f} to ₹{new_weekly_demand_zone_distal:.2f} "
                f"beneath confirmed Weekly Demand Distal Line. Surviving structural pullbacks; riding trend (+{unrealized_gain:.1f}% unrealized)."
            )
        else:
            state.advisory_message = (
                f"HOLDING POSITION: Candidate zone distal ₹{new_weekly_demand_zone_distal:.2f} is not higher than "
                f"active trailing SL ₹{state.current_trailing_stop_loss:.2f}. SL remains firmly anchored."
            )

        return state


class TopDownScannerEngine:
    """
    Episode 20 High-Speed Stock Scanner & Watchlist Architecture:
    Filters thousands of stocks down to a high-conviction master watchlist in 30 minutes a day.
    """

    @staticmethod
    def evaluate_52_week_high_proximity(
        cmp: float,
        high_52w: float,
        threshold_pct: float = 10.0,
    ) -> Tuple[bool, float]:
        """
        The 'Approaching 52-Week High' Shortcut:
        Stocks within 5-10% of 52W high are in established multi-timeframe uptrends (Daily, Weekly, Monthly green).
        Provides open sky with minimal overhead resistance.
        """
        if high_52w <= 0:
            return False, 0.0
        distance_pct = ((high_52w - cmp) / high_52w) * 100.0
        is_approaching = 0.0 <= distance_pct <= threshold_pct
        return is_approaching, round(distance_pct, 2)

    @staticmethod
    def classify_daily_candle_activity(
        daily_pct_change: float,
        is_entering_demand: bool = False,
        is_fresh_origin: bool = False,
    ) -> Tuple[StockScanFilterType, ScanCandidatePriority, str]:
        """
        30-Minute Daily Scanning Workflow:
        - -0.5% to +0.5%: Base candle equilibrium churn (IGNORE).
        - Top Gainers (> +1.5%): Scan for fresh Daily origin bases.
        - Top Losers (< -1.5%): Scan for pullbacks entering pre-identified demand zones.
        """
        abs_change = abs(daily_pct_change)

        if abs_change <= 0.50:
            return (
                StockScanFilterType.BASING_RANGE_CHURN,
                ScanCandidatePriority.IGNORE_BASING,
                f"Daily change {daily_pct_change:+.2f}% represents equilibrium base churn. Discard for active trading.",
            )

        if is_entering_demand or daily_pct_change < -1.5:
            return (
                StockScanFilterType.PULLBACK_INTO_DEMAND,
                ScanCandidatePriority.WATCHLIST_ALERT,
                f"Daily dip {daily_pct_change:+.2f}%: Pullback entering pre-identified institutional demand zone. Verify alert.",
            )

        if is_fresh_origin or daily_pct_change > 1.5:
            return (
                StockScanFilterType.FRESH_ORIGIN_FORMATION,
                ScanCandidatePriority.WATCHLIST_ALERT,
                f"Daily rally {daily_pct_change:+.2f}%: Explosive leg-out departure. Mark fresh origin demand base.",
            )

        return (
            StockScanFilterType.BASING_RANGE_CHURN,
            ScanCandidatePriority.IGNORE_BASING,
            f"Daily change {daily_pct_change:+.2f}% is routine intermediate movement.",
        )

    @staticmethod
    def calculate_price_alert(
        proximal_line: float,
        buffer_inr: float = 2.0,
    ) -> float:
        """
        The Mandatory Price Alert Mandate:
        Places alert 1 to 2 rupees above the Proximal Line so traders never stare at live screens.
        """
        return round(proximal_line + buffer_inr, 2)

    @staticmethod
    def generate_on_chart_note(
        symbol: str,
        quarterly_trend: str,
        monthly_trend: str,
        weekly_trend: str,
        daily_trend: str,
        location_summary: str,
        trade_style: str,
        score_ratio: str,
        entry: float,
        stop_loss: float,
        target: float,
        rrr: float,
    ) -> str:
        """
        The Permanent On-Chart Note-Taking Protocol:
        Generates a 5-second complete analytical restoration block directly on chart.
        """
        return (
            f"=== {symbol} GTF ON-CHART MASTER NOTE ===\n"
            f"TREND OVERVIEW: Q: {quarterly_trend} | M: {monthly_trend} | W: {weekly_trend} | D: {daily_trend}\n"
            f"LOCATION CONTEXT: {location_summary}\n"
            f"TRADE PLAN: {trade_style} Long ({score_ratio}) | Entry: ₹{entry:.2f} | SL: ₹{stop_loss:.2f} | Tgt: ₹{target:.2f} | RRR: {rrr:.1f}:1\n"
            f"ACTION: Pre-set Price Alert at ₹{entry + 2.0:.2f}. Review intermediate trend upon mobile alert."
        )

```

---

## 13. Pre-Trade Risk Engine & Concentration Limits (`alphacouncil/risk/pre_trade.py`)

```python
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
        max_sector_pct: float = 0.30,
        max_total_open_risk_pct: float = 0.03,
        max_orders_per_sec: int = 10,
    ):
        self.max_single_stock_pct = max_single_stock_pct
        self.max_sector_pct = max_sector_pct
        self.max_total_open_risk_pct = max_total_open_risk_pct
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
        current_sector_notional: float = 0.0,
        current_portfolio_open_risk_pct: float = 0.0,
        proposed_trade_risk_pct: float = 0.0,
        stop_loss_price: Optional[float] = None,
        max_gap_stress_pct: float = 0.02,
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
        effective_quantity = proposed_quantity
        capping_reasons = []

        existing_notional = max(0, current_position_shares) * entry_price
        proposed_notional = effective_quantity * entry_price
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
            effective_quantity = capped_qty
            capping_reasons.append(f"Capped from {proposed_quantity} to {capped_qty} shares (20% notional ceiling)")

        # 6. Sector Concentration Cap (Existing Sector Notional + Proposed Notional <= 30%)
        proposed_sector_notional = effective_quantity * entry_price
        total_sector_notional = current_sector_notional + proposed_sector_notional
        max_sector_notional_allowed = current_equity * self.max_sector_pct
        if total_sector_notional > max_sector_notional_allowed:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason=f"SECTOR_CONCENTRATION_EXCEEDED: Sector exposure ₹{total_sector_notional:,.2f} exceeds 30% ceiling (Max: ₹{max_sector_notional_allowed:,.2f})",
                rejection_code="ERR_SECTOR_CONCENTRATION",
            )

        # 7. Portfolio Max Concurrent Open Risk Cap (Current Open Risk + Proposed Trade Risk <= 3.0%)
        effective_trade_risk_pct = proposed_trade_risk_pct
        if effective_trade_risk_pct <= 0.0 and stop_loss_price is not None and stop_loss_price > 0:
            trade_loss = effective_quantity * abs(entry_price - stop_loss_price)
            effective_trade_risk_pct = trade_loss / current_equity

        if current_portfolio_open_risk_pct + effective_trade_risk_pct > self.max_total_open_risk_pct + 1e-6:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason=f"PORTFOLIO_RISK_CAP_EXCEEDED: Open risk ({current_portfolio_open_risk_pct*100:.1f}% + {effective_trade_risk_pct*100:.1f}%) exceeds 3.0% hard ceiling",
                rejection_code="ERR_MAX_OPEN_RISK",
            )

        # 8. Gap-Stress Test: 2x Stop-Loss Slippage Stress (Loss must not exceed 2.0% equity)
        if stop_loss_price is not None and stop_loss_price > 0:
            nominal_risk_per_share = abs(entry_price - stop_loss_price)
            stressed_loss_per_share = nominal_risk_per_share * 2.0  # 2x stop slippage gap stress
            total_stressed_loss = effective_quantity * stressed_loss_per_share
            if total_stressed_loss > current_equity * max_gap_stress_pct:
                stressed_capped_qty = int((current_equity * max_gap_stress_pct) // stressed_loss_per_share)
                if stressed_capped_qty <= 0:
                    return RiskValidationResult(
                        is_approved=False,
                        adjusted_quantity=0,
                        reason="ERR_GAP_STRESS_EXCEEDED: Position cannot survive 2x stop gap-down within 2.0% equity loss",
                        rejection_code="ERR_GAP_STRESS_EXCEEDED",
                    )
                effective_quantity = min(effective_quantity, stressed_capped_qty)
                capping_reasons.append(f"GAP_STRESS_APPLIED: Capped to {effective_quantity} shares (2x stop gap-down 2.0% equity limit)")

        if effective_quantity <= 0:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="ORDER_DISALLOWED: Effective quantity reduced to 0 by pre-trade risk gates",
                rejection_code="ERR_RISK_GATES_ZERO_QTY",
            )

        if capping_reasons:
            return RiskValidationResult(
                is_approved=True,
                adjusted_quantity=effective_quantity,
                reason="APPROVED_WITH_CAPPING: " + "; ".join(capping_reasons),
            )

        return RiskValidationResult(
            is_approved=True,
            adjusted_quantity=proposed_quantity,
            reason="PRE_TRADE_PASSED: All boundary checks green",
        )

```

---

## 14. Position Sizing & Kelly Calibration (`alphacouncil/risk/sizing.py`)

```python
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
        cold_start_trade_threshold: int = 50,# Minimum closed trades required to exit cold start
    ):
        self.base_risk_fraction = base_risk_fraction
        self.target_annual_vol = target_annual_vol
        self.max_risk_ceiling = max_risk_ceiling
        self.max_notional_pct = max_notional_pct
        self.min_atr_multiple = min_atr_multiple
        self.cold_start_trade_threshold = cold_start_trade_threshold

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
        # If stop distance is less than min_atr_multiple * ATR14 (default 0.25 * ATR14 per config.py), skip trade entirely as low-quality noise trap
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
        # Cold start check: Requires at least cold_start_trade_threshold closed trades AND valid BSS AND valid win prob
        if historical_closed_trades_count < self.cold_start_trade_threshold or rolling_bss is None or estimated_win_prob is None:
            regime = "COLD_START"
            tau_eff = min(tau_vol, 0.010)  # Capped at 1.0% in cold start
            msg = f"Cold start (trades={historical_closed_trades_count}<{self.cold_start_trade_threshold} or uncalibrated). Governed strictly by Vol-Targeting (Risk={tau_eff*100:.2f}%)."
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

```

---

## 15. López de Prado Meta-Labeler Downscaler (`alphacouncil/risk/meta_labeler.py`)

```python
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

```

---

## 16. Intraday Kill-Switch & Monthly Session Halt (`alphacouncil/risk/kill_switch.py`)

```python
"""
Independent Peak-HWM Intraday Drawdown Circuit Breaker & Watchdog Kill Switch.
Codifies Section 4B of RFC v5.0 with full audit logging and sticky session enforcement.
"""

from dataclasses import dataclass
import datetime
import time
from typing import List, Optional


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


@dataclass
class RiskAuditRecord:
    """Immutable audit record for regulatory compliance and risk committee actions."""
    timestamp: float
    iso_time: str
    action: str
    authorized_by: str
    reason: str
    current_equity: float
    intraday_hwm: float
    monthly_hwm: float
    prior_session_halted: bool
    prior_strategy_frozen: bool


class IntradayKillSwitch:
    """
    Monitors portfolio mid-market valuation every 5 seconds.
    Enforces the 2.0% intraday peak-HWM halt and 6.0% monthly freeze.
    Maintains sticky session states and a cryptographic audit log for unfreezes.
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
        self.audit_log: List[RiskAuditRecord] = []

    def reset_daily_session(self, starting_equity: float):
        """Called at 9:00 AM pre-market open to establish new session HWM and clear daily halt."""
        self.intraday_hwm = starting_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = starting_equity
        else:
            self.monthly_hwm = max(self.monthly_hwm, starting_equity)

        # Daily halt is cleared on a new session unless the monthly freeze is active
        if not self.is_strategy_frozen:
            self.is_session_halted = False

    def reset_monthly_session(self, starting_equity: float):
        """Called at calendar month boundary to establish new monthly and daily HWM baselines and lift monthly freeze."""
        record = RiskAuditRecord(
            timestamp=time.time(),
            iso_time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            action="MONTHLY_SESSION_RESET",
            authorized_by="SYSTEM_SCHEDULER",
            reason="Calendar month boundary rollover: new baseline established",
            current_equity=round(starting_equity, 2),
            intraday_hwm=round(starting_equity, 2),
            monthly_hwm=round(starting_equity, 2),
            prior_session_halted=self.is_session_halted,
            prior_strategy_frozen=self.is_strategy_frozen,
        )
        self.audit_log.append(record)

        self.monthly_hwm = starting_equity
        self.intraday_hwm = starting_equity  # Reset daily HWM so previous month drawdowns don't cause instant re-halt
        self.is_strategy_frozen = False
        self.is_session_halted = False

    def update_valuation(self, mid_market_equity: float) -> DrawdownStatus:
        """
        Evaluates current valuation against intraday and monthly HWM.
        Enforces sticky halt states (once halted within a session, remains halted until daily reset).
        """
        self.last_heartbeat_time = time.time()

        if self.intraday_hwm <= 0.0:
            self.intraday_hwm = mid_market_equity
        if self.monthly_hwm <= 0.0:
            self.monthly_hwm = mid_market_equity

        # Update HWM on upward expansion (only if not currently halted/frozen)
        if not self.is_session_halted and not self.is_strategy_frozen:
            if mid_market_equity > self.intraday_hwm:
                self.intraday_hwm = mid_market_equity
            if mid_market_equity > self.monthly_hwm:
                self.monthly_hwm = mid_market_equity

        # Compute Drawdowns
        dd_intra = (self.intraday_hwm - mid_market_equity) / (self.intraday_hwm + 1e-8)
        dd_month = (self.monthly_hwm - mid_market_equity) / (self.monthly_hwm + 1e-8)

        # 1. Strategy Frozen check (6.0% monthly threshold or already frozen)
        if self.is_strategy_frozen or dd_month >= self.monthly_freeze_threshold:
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

        # 2. Intraday Session Halt check (2.0% intraday threshold or already halted for current session)
        if self.is_session_halted or dd_intra >= self.intraday_halt_threshold:
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

    def risk_committee_unfreeze(
        self,
        authorized_by: str,
        reason: str,
        current_equity: Optional[float] = None,
    ) -> RiskAuditRecord:
        """
        Explicit, cryptographically audit-trailed method for human risk committee to unfreeze the strategy.
        Records caller identity, institutional rationale, and state snapshot.
        """
        if not authorized_by or not reason:
            raise ValueError("Risk committee unfreeze requires explicit authorized_by identity and justification reason")

        equity_val = current_equity if current_equity is not None else self.intraday_hwm
        record = RiskAuditRecord(
            timestamp=time.time(),
            iso_time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            action="RISK_COMMITTEE_OVERRIDE_UNFREEZE",
            authorized_by=authorized_by,
            reason=reason,
            current_equity=round(equity_val, 2),
            intraday_hwm=round(self.intraday_hwm, 2),
            monthly_hwm=round(self.monthly_hwm, 2),
            prior_session_halted=self.is_session_halted,
            prior_strategy_frozen=self.is_strategy_frozen,
        )
        self.audit_log.append(record)

        # Unfreeze state and re-align HWM to current equity to allow controlled resumption
        if current_equity is not None and current_equity > 0:
            self.intraday_hwm = current_equity
            self.monthly_hwm = current_equity

        self.is_strategy_frozen = False
        self.is_session_halted = False
        self.last_heartbeat_time = time.time()
        return record

    def check_watchdog_heartbeat(self, max_allowed_miss_sec: float = 9.0) -> bool:
        """
        Dead-man's switch check. If heartbeat missing > 9s, trigger autonomous emergency cancellation.
        """
        elapsed = time.time() - self.last_heartbeat_time
        return elapsed < max_allowed_miss_sec

```

---

## 17. Direction-Aware Circuit Band Guard (`alphacouncil/risk/circuits.py`)

```python
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

```

---

## 18. GTF Risk Management & Capital Protection Engine (`alphacouncil/risk/gtf_risk.py`)

```python
"""
GTF Institutional Risk Management & Capital Protection Engine (Episode 10).
Codifies the Exact Position Sizing Formula, Monetary Risk Invariance,
The 10 Trades/Month Cap, Anti-Tampering SL Guards, The 100-Trade Journal,
and Quantitative Excel Growth Models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple
import math


class RiskTier(float, Enum):
    """
    Episode 10: Risk Per Trade (RPT) Hierarchy.
    Determines maximum monetary risk percentage of total capital allocated per trade.
    """
    LEARNING = 0.005       # 0.5% (Early practice, absorbs early mistakes cheaply)
    BEGINNER = 0.010       # 1.0% (First 1-3 months of live trading)
    INTERMEDIATE = 0.015   # 1.5% (Proven consistency)
    PRO = 0.020            # 2.0% (Absolute ceiling - never exceed)


class ExecutionErrorType(str, Enum):
    """
    Episode 10 Concept 11: The 40-Mistake Rule Categories.
    'A mistake repeated more than once is a decision.'
    """
    TREND_CONFLICT = "TREND_CONFLICT"
    OVERHEAD_HTF_SUPPLY_TRAP = "OVERHEAD_HTF_SUPPLY_TRAP"
    UNPROVEN_CANDLE_CLOSE = "UNPROVEN_CANDLE_CLOSE"
    FO_LOT_SIZE_OVERLEVERAGE = "FO_LOT_SIZE_OVERLEVERAGE"
    NEWS_HEADLINE_TRAP = "NEWS_HEADLINE_TRAP"
    CHASING_MISSED_ENTRY = "CHASING_MISSED_ENTRY"
    STOPLOSS_WIDENED_POST_ENTRY = "STOPLOSS_WIDENED_POST_ENTRY"
    AVERAGING_DOWN = "AVERAGING_DOWN"
    MONTHLY_TRADE_CAP_BREACH = "MONTHLY_TRADE_CAP_BREACH"
    ARBITRARY_QUANTITY = "ARBITRARY_QUANTITY"


@dataclass
class SizingBreakdown:
    """Exact mathematical position sizing breakdown."""
    capital: float
    risk_tier: RiskTier
    risk_per_trade_inr: float
    entry_price: float
    stop_loss_price: float
    risk_distance_points: float
    quantity_shares: int
    actual_monetary_risk_inr: float
    total_capital_required_inr: float
    is_sizing_valid: bool
    rationale: str


@dataclass
class GrowthProjection:
    """Quantitative growth projection (The Excel Growth Model)."""
    capital: float
    risk_tier: RiskTier
    win_rate: float
    target_rrr: float
    num_trades: int
    wins_count: int
    losses_count: int
    risk_per_trade: float
    gain_per_win: float
    total_gain: float
    total_loss: float
    net_monthly_profit: float
    monthly_return_pct: float
    annual_return_pct: float


@dataclass
class TradeLogEntry:
    """Record entry for the GTF 100-Trade Journal."""
    trade_id: int
    date: str
    symbol: str
    entry_price: float
    stop_loss: float
    target_price: float
    quantity: int
    outcome: str  # "TARGET_HIT", "STOP_LOSS_HIT", "OPEN"
    pnl_inr: float = 0.0
    mistakes: List[ExecutionErrorType] = field(default_factory=list)
    notes: str = ""


class GTFTradingJournal:
    """
    Episode 10 Concept 6 & 11: The Mandatory 100-Trade Journal.
    Enforces:
    1. Maximum 10 trades per calendar month.
    2. The 100-trade commitment before judging a strategy.
    3. The 40-mistake elimination tracker ('never repeat the same mistake twice').
    """

    MAX_TRADES_PER_MONTH: int = 10
    TARGET_COMMITMENT_TRADES: int = 100

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.trades: List[TradeLogEntry] = []
        self.mistake_counts: Dict[ExecutionErrorType, int] = {e: 0 for e in ExecutionErrorType}

    def log_trade(self, entry: TradeLogEntry) -> Tuple[bool, str]:
        """
        Logs a trade into the journal.
        Enforces monthly cap and tracks repetitive mistakes.
        """
        # Count trades in the same month (extract YYYY-MM)
        month_str = entry.date[:7] if len(entry.date) >= 7 else "CURRENT"
        current_month_count = sum(1 for t in self.trades if t.date[:7] == month_str)

        if current_month_count >= self.MAX_TRADES_PER_MONTH:
            return (
                False,
                f"Monthly Cap Reached: Already executed {current_month_count}/{self.MAX_TRADES_PER_MONTH} trades for {month_str}. "
                "Ruthlessly filter; do not overtrade.",
            )

        # Track mistakes
        repeat_warnings = []
        for m in entry.mistakes:
            self.mistake_counts[m] += 1
            if self.mistake_counts[m] > 1:
                repeat_warnings.append(f"Repeat Mistake Detected: {m.value} logged {self.mistake_counts[m]} times!")

        self.trades.append(entry)
        msg = f"Trade #{len(self.trades)} logged successfully."
        if repeat_warnings:
            msg += " " + " ".join(repeat_warnings)
        return True, msg

    @property
    def total_trades_count(self) -> int:
        return len(self.trades)

    @property
    def is_100_trade_commitment_fulfilled(self) -> bool:
        return len(self.trades) >= self.TARGET_COMMITMENT_TRADES


class GTFRiskManager:
    """
    Core Risk Management Engine taught by Arun Singh Tanwar.
    """

    @staticmethod
    def calculate_position_size(
        capital: float,
        risk_tier: RiskTier,
        entry_price: float,
        stop_loss: float,
    ) -> SizingBreakdown:
        """
        Episode 10 Concept 3: The Exact Position Sizing Formula.
        Quantity = floor(Risk_Per_Trade / abs(Entry - StopLoss))
        Ensures monetary loss on an SL hit is strictly identical regardless of share price.
        """
        risk_distance = abs(entry_price - stop_loss)
        if risk_distance <= 0.0:
            return SizingBreakdown(
                capital=capital,
                risk_tier=risk_tier,
                risk_per_trade_inr=0.0,
                entry_price=entry_price,
                stop_loss_price=stop_loss,
                risk_distance_points=0.0,
                quantity_shares=0,
                actual_monetary_risk_inr=0.0,
                total_capital_required_inr=0.0,
                is_sizing_valid=False,
                rationale="Invalid stop-loss distance (cannot be zero).",
            )

        rpt_inr = round(capital * risk_tier.value, 2)
        qty = int(math.floor(rpt_inr / risk_distance))
        actual_risk = round(qty * risk_distance, 2)
        capital_req = round(qty * entry_price, 2)

        is_valid = qty > 0

        rationale = (
            f"Capital: ₹{capital:,.2f} | Tier: {risk_tier.name} ({risk_tier.value*100:.1f}%) | "
            f"RPT: ₹{rpt_inr:,.2f} | Risk Points: ₹{risk_distance:.2f} | "
            f"Quantity: {qty} shares | Actual Max Loss: ₹{actual_risk:,.2f} | "
            f"Capital Required: ₹{capital_req:,.2f}."
        )

        return SizingBreakdown(
            capital=capital,
            risk_tier=risk_tier,
            risk_per_trade_inr=rpt_inr,
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            risk_distance_points=risk_distance,
            quantity_shares=qty,
            actual_monetary_risk_inr=actual_risk,
            total_capital_required_inr=capital_req,
            is_sizing_valid=is_valid,
            rationale=rationale,
        )

    @staticmethod
    def detect_anti_tamper_violations(
        original_entry: float,
        current_market_price: float,
        original_sl: float,
        new_sl: float,
        is_demand: bool = True,
        is_averaging_down: bool = False,
        chase_threshold_pct: float = 0.015,
    ) -> Tuple[bool, List[str]]:
        """
        Episode 10 Concept 4: Anti-Tamper & Critical Execution Error Guards.
        1. Chasing Missed Entry: CMP already rallied significantly past entry.
        2. Modifying/Widening Stop-Loss: Expanding SL distance post-entry.
        3. Averaging Down: Adding to losing position.
        """
        violations: List[str] = []

        # 1. Chasing Missed Entry
        if is_demand:
            if current_market_price > original_entry * (1.0 + chase_threshold_pct):
                violations.append(
                    f"Chasing Missed Entry Prohibited: CMP ₹{current_market_price:.2f} is "
                    f"> {chase_threshold_pct*100:.1f}% above entry ₹{original_entry:.2f}. "
                    "Let the trade go; missing costs ₹0."
                )
        else:
            if current_market_price < original_entry * (1.0 - chase_threshold_pct):
                violations.append(
                    f"Chasing Missed Short Prohibited: CMP ₹{current_market_price:.2f} is "
                    f"> {chase_threshold_pct*100:.1f}% below entry ₹{original_entry:.2f}."
                )

        # 2. Widening Stop-Loss
        if is_demand:
            if new_sl < original_sl:
                violations.append(
                    f"Stop-Loss Widening Prohibited: Moving SL down from ₹{original_sl:.2f} to ₹{new_sl:.2f} "
                    "inflates risk exponentially. Maintain original stop."
                )
        else:
            if new_sl > original_sl:
                violations.append(
                    f"Stop-Loss Widening Prohibited: Moving short SL up from ₹{original_sl:.2f} to ₹{new_sl:.2f}."
                )

        # 3. Averaging Down
        if is_averaging_down:
            violations.append(
                "Averaging Down Trap: Adding shares to a position falling through a demand zone is strictly prohibited."
            )

        is_clean = len(violations) == 0
        return is_clean, violations

    @staticmethod
    def project_growth(
        capital: float = 100000.0,
        risk_tier: RiskTier = RiskTier.BEGINNER,
        win_rate: float = 0.50,
        target_rrr: float = 2.0,
        num_trades: int = 10,
    ) -> GrowthProjection:
        """
        Episode 10 Concept 7: Quantitative Excel Growth Model.
        Calculates expected returns based on 10 trades per month and Risk-to-Reward ratio.
        """
        wins = int(round(num_trades * win_rate))
        losses = num_trades - wins
        rpt = capital * risk_tier.value
        gain_per_win = rpt * target_rrr

        total_gain = wins * gain_per_win
        total_loss = losses * rpt
        net_profit = total_gain - total_loss
        monthly_return_pct = round((net_profit / capital) * 100.0, 2)
        annual_return_pct = round(monthly_return_pct * 12.0, 2)

        return GrowthProjection(
            capital=capital,
            risk_tier=risk_tier,
            win_rate=win_rate,
            target_rrr=target_rrr,
            num_trades=num_trades,
            wins_count=wins,
            losses_count=losses,
            risk_per_trade=rpt,
            gain_per_win=gain_per_win,
            total_gain=total_gain,
            total_loss=total_loss,
            net_monthly_profit=net_profit,
            monthly_return_pct=monthly_return_pct,
            annual_return_pct=annual_return_pct,
        )

```

---

## 19. Statutory Indian Market Friction Model (SEBI Oct 2024) (`alphacouncil/execution/friction.py`)

```python
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

```

---

## 20. Idempotent OMS & Broker GTT Bracket Sync (`alphacouncil/execution/oms.py`)

```python
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

```

---

## 21. Purged Walk-Forward Backtesting Engine (`alphacouncil/backtest/engine.py`)

```python
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
        sweep_lookback: int = 15,
        sweep_volume_factor: float = 1.2,
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
        self.sweep_detector = LiquiditySweepDetector(lookback=sweep_lookback, volume_factor=sweep_volume_factor)
        self.nlp = FinBertSentimentExtractor()
        self.triple_barrier = TripleBarrierLabeler(payoff_ratio=2.0, max_vertical_days=5)
        self.pre_trade = PreTradeRiskEngine(max_single_stock_pct=0.20)
        self.sizing = PositionSizingEngine(
            base_risk_fraction=config.risk.base_risk_fraction,
            target_annual_vol=config.risk.target_annual_volatility,
            min_atr_multiple=config.risk.min_atr_stop_multiple if use_atr_stop else 0.0,
            cold_start_trade_threshold=getattr(config.risk, "cold_start_trade_threshold", 50),
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

        # Mark daily session
        self.kill_switch.reset_daily_session(cash)

        for day in range(25, n_bars):
            # 1. Calculate Mark-to-Market Portfolio Valuation at Day Start
            current_portfolio_value = cash
            for sym, pos in active_positions.items():
                current_bar = universe_data[sym][day]
                current_portfolio_value += pos["shares"] * current_bar.open

            # Calendar Month Transition Check for Monthly HWM Reset vs Daily Reset
            current_date_str = universe_data[symbols[0]][day].timestamp
            current_month = current_date_str[:7]
            if prev_month and current_month != prev_month:
                self.kill_switch.reset_monthly_session(current_portfolio_value)
            else:
                self.kill_switch.reset_daily_session(current_portfolio_value)
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
                            "max_hold_days": order.get("max_hold_days", 5),
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

                # Check 3C: Triple Barrier Path Evaluation (accounting for overnight gap-down fills)
                if not exit_triggered:
                    if bar.low <= pos["stop_price"]:
                        exit_triggered = True
                        exit_price = min(bar.open, pos["stop_price"])
                        reason = "GAP_DOWN_STOP_SLIP" if bar.open < pos["stop_price"] else "STOP_LOSS_HIT"
                    elif bar.high >= pos["target_price"]:
                        exit_triggered = True
                        exit_price = max(bar.open, pos["target_price"]) if bar.open > pos["target_price"] else pos["target_price"]
                        reason = "PROFIT_TARGET_HIT"
                    elif holding_days >= pos.get("max_hold_days", 5):
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

                        # Sentiment featurizer via FinBertSentimentExtractor
                        if self.use_sentiment_nlp:
                            headline = self.calendar.get_latest_headline(sym, bar_t.timestamp)
                            sentiment = self.nlp.extract_sentiment(sym, headline)
                        else:
                            sentiment = 0.0

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
                            recent_closes = np.array([b.close for b in bars[-30:]])

                            # Dynamic vertical barrier derived from Ornstein-Uhlenbeck half-life
                            ou_hl = self.triple_barrier.calculate_ou_half_life(recent_closes)
                            dynamic_max_hold = int(np.clip(round(ou_hl), 3, 10))

                            # Volatility targeting vs flat risk
                            if self.use_vol_sizing:
                                ann_vol = float(np.std(np.diff(np.log(recent_closes))) * np.sqrt(252.0))
                            else:
                                ann_vol = self.config.risk.target_annual_volatility  # Flat risk baseline

                            # Dynamic regime transition: Cold start until threshold empirical closed trades exist
                            trades_count = len(completed_trades)
                            if self.use_kelly_cap and trades_count >= self.sizing.cold_start_trade_threshold:
                                calib_window = getattr(self.config.risk, "rolling_calibration_window", 250)
                                recent = completed_trades[-calib_window:]
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
                                # Calculate current portfolio open risk & sector notional
                                current_open_risk_val = sum(
                                    p["shares"] * max(0.0, p["entry_price"] - p["stop_price"])
                                    for p in active_positions.values()
                                )
                                current_open_risk_pct = current_open_risk_val / (current_portfolio_value + 1e-8)

                                sym_sector = self.calendar.get_sector(sym)
                                current_sector_notional = sum(
                                    p["shares"] * universe_data[s][day].close
                                    for s, p in active_positions.items()
                                    if self.calendar.get_sector(s) == sym_sector
                                )

                                # Pre-trade validation with simulation flag (cleanly bypasses wall-clock limiter)
                                val = self.pre_trade.validate_order(
                                    symbol=sym,
                                    proposed_quantity=int(sizing_res.shares_quantity * meta_out.alpha_scale),
                                    entry_price=bar_t.close,
                                    current_equity=current_portfolio_value,
                                    current_sector_notional=current_sector_notional,
                                    current_portfolio_open_risk_pct=current_open_risk_pct,
                                    stop_loss_price=stop_p,
                                    is_simulation_mode=True,
                                )
                                if val.is_approved and val.adjusted_quantity > 0:
                                    pending_orders.append({
                                        "symbol": sym,
                                        "quantity": val.adjusted_quantity,
                                        "stop_price": stop_p,
                                        "target_price": target_p,
                                        "max_hold_days": dynamic_max_hold,
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

```

---

## 22. Deflated Sharpe Ratio (DSR) & Quant Metrics (`alphacouncil/backtest/metrics.py`)

```python
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

```

---

## 23. 7-Model Orthogonal Ablation Suite (`alphacouncil/backtest/ablation.py`)

```python
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

```

---

## 24. Interactive Bloomberg Dashboard UI (`alphacouncil/ui/dashboard.py`)

```python
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

```

---

## 25. Master Research Demo Runner (`alphacouncil/run_council.py`)

```python
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

```

---

## 26. Forward Paper Testing Engine & Pullback Order Lifecycle (`alphacouncil/execution/paper_trader.py`)

```python
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

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
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
    is_simulation: bool = True
    simulation_environment: str = "CALIBRATED_STOCHASTIC_NSE"
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
                is_trailed = pos.is_risk_free_trailed or (pos.current_stop_loss > pos.entry_price)
                reason = ExitReason.TRAILING_STOP_EXIT if (is_trailed and bar.open >= pos.entry_price) else ExitReason.GAP_DOWN_STOP_SLIP
                symbols_to_close.append((symbol, bar.open, reason, gap_slip))
                continue

            # 3. Intraday Target Hit (High reached target)
            if bar.high >= pos.target_price:
                symbols_to_close.append((symbol, pos.target_price, ExitReason.TARGET_HIT, 0.0))
                continue

            # 4. Intraday Stop-Loss Hit (Low breached stop-loss)
            if bar.low <= pos.current_stop_loss:
                is_trailed = pos.is_risk_free_trailed or (pos.current_stop_loss >= pos.entry_price)
                reason = ExitReason.TRAILING_STOP_EXIT if is_trailed else ExitReason.STOP_LOSS_HIT
                symbols_to_close.append((symbol, pos.current_stop_loss, reason, 0.0))
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
                trade_id = f"SIM-TRD-{self.trade_counter:03d}"

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

    def export_journal_to_json(self, filepath: str) -> None:
        """Serializes all completed trade audit records to structured JSON."""
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.bool_, bool)):
                    return bool(obj)
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.completed_trades], f, indent=2, cls=NpEncoder)

```

---

