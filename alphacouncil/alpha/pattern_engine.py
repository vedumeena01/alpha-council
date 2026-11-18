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
