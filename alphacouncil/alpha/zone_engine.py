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

        if base_score < 6.0:
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

        # 11. Mathematical Position Sizing & Rupee-Risk Invariance (Ep 10)
        risk_per_share = abs(execution_zone.entry_price - execution_zone.stop_loss)
        if risk_per_share <= 0:
            risk_per_share = abs(execution_zone.proximal_line - execution_zone.distal_line)

        monetary_risk = capital * (risk_per_trade_pct / 100.0)
        calculated_qty = int(monetary_risk // risk_per_share) if risk_per_share > 0 else 0

        if calculated_qty <= 0:
            rejection_reasons.append(f"Position Sizing: Risk per share ₹{risk_per_share:.2f} exceeds allowable monetary risk ₹{monetary_risk:.2f} (Quantity = 0).")
        else:
            audit_checks_passed.append(f"Position Sizing: {calculated_qty} shares planned at exact ₹{monetary_risk:.2f} risk.")

        # 12. Target Expectation & RRR Expansion (Ep 4, 8, 15)
        if origin_quality == OriginQuality.PRISTINE_ORIGIN:
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
