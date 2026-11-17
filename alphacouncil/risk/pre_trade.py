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
    ) -> RiskValidationResult:
        """
        Validates proposed trade against hard pre-trade parameters.
        """
        now = time.time()

        # 1. Rate-Limiting & Anti-Runaway Loop Check
        self.order_timestamps = [t for t in self.order_timestamps if now - t < 1.0]
        if len(self.order_timestamps) >= self.max_orders_per_sec:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="RATE_LIMIT_EXCEEDED: Maximum 10 order actions per second reached",
                rejection_code="ERR_RATE_LIMIT",
            )
        self.order_timestamps.append(now)

        # 2. Basic Tick / Step Size Sanity
        if proposed_quantity <= 0 or entry_price <= 0.0:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="INVALID_PARAMETERS: Quantity and Price must be positive",
                rejection_code="ERR_INVALID_PARAMS",
            )

        # 3. Fail-Closed Cash / Equity Check
        if current_equity <= 0.0:
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="FAIL_CLOSED: Portfolio equity unresolvable or negative",
                rejection_code="ERR_ACCOUNT_UNRESOLVED",
            )

        # 4. Reduce-Only Verification
        if is_reduce_only and proposed_quantity > abs(current_position_shares):
            return RiskValidationResult(
                is_approved=False,
                adjusted_quantity=0,
                reason="REDUCE_ONLY_VIOLATION: Order increases exposure instead of reducing",
                rejection_code="ERR_REDUCE_ONLY",
            )

        # 5. Single-Stock Concentration Cap (Max 20% Notional)
        proposed_notional = proposed_quantity * entry_price
        max_notional_allowed = current_equity * self.max_single_stock_pct

        if proposed_notional > max_notional_allowed:
            capped_qty = int(max_notional_allowed // entry_price)
            if capped_qty <= 0:
                return RiskValidationResult(
                    is_approved=False,
                    adjusted_quantity=0,
                    reason=f"CONCENTRATION_EXCEEDED: Single stock notional exceeds 20% cap (₹{max_notional_allowed:,.2f})",
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
