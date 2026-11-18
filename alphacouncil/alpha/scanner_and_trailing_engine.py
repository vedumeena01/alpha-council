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
