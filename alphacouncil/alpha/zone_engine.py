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

from dataclasses import dataclass
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


class TimeframeTier(str, Enum):
    MONTHLY = "MONTHLY"    # Highest institutional dominance (Weight 4.0)
    WEEKLY = "WEEKLY"      # Intermediate institutional swing (Weight 3.0)
    DAILY = "DAILY"        # Standard positional baseline (Weight 2.0)
    M125 = "125M"          # Exact NSE session partition 3 bars/day (Weight 1.5)
    M75 = "75M"            # Exact NSE session partition 5 bars/day (Weight 1.25)
    INTRADAY = "INTRADAY"  # 5m-60m noise vulnerable (Weight 1.0)


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


class DemandSupplyEngine:
    """
    Core Price Action Engine trained on Institutional Order Flow,
    Demand-Supply Imbalances, Normal vs. Exceptional Zone Marking,
    Wick-to-Wick Mapping, Timeframe Hierarchy, The Closing Concept,
    Gap+Base Identity, Origin Isolation, and Trading Psychology.
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
