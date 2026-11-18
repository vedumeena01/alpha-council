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
