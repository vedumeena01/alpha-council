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
        if is_entry:
            if dist_to_upper_pct <= self.proximity_threshold_pct:
                return CircuitCheckResult(
                    can_enter=False,
                    should_emergency_exit=False,
                    proximity_pct_upper=round(dist_to_upper_pct * 100, 2),
                    proximity_pct_lower=round(dist_to_lower_pct * 100, 2),
                    reason=f"ENTRY_BLOCKED: Price is within {dist_to_upper_pct*100:.2f}% of Upper Circuit ({upper_circuit}). Exhaustion risk.",
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
