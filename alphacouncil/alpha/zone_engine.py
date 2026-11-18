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
