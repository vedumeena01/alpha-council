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
