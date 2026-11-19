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
        existing_notional = max(0, current_position_shares) * entry_price
        proposed_notional = proposed_quantity * entry_price
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
            return RiskValidationResult(
                is_approved=True,
                adjusted_quantity=capped_qty,
                reason=f"APPROVED_WITH_CAPPING: Quantity capped from {proposed_quantity} to {capped_qty} shares (20% notional ceiling)",
            )

        # 6. Sector Concentration Cap (Existing Sector Notional + Proposed Notional <= 30%)
        total_sector_notional = current_sector_notional + proposed_notional
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
            trade_loss = proposed_quantity * abs(entry_price - stop_loss_price)
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
            total_stressed_loss = proposed_quantity * stressed_loss_per_share
            if total_stressed_loss > current_equity * max_gap_stress_pct:
                stressed_capped_qty = int((current_equity * max_gap_stress_pct) // stressed_loss_per_share)
                return RiskValidationResult(
                    is_approved=True if stressed_capped_qty > 0 else False,
                    adjusted_quantity=stressed_capped_qty,
                    reason=f"GAP_STRESS_APPLIED: Quantity scaled down to {stressed_capped_qty} shares to survive 2x stop gap-down within 2.0% equity loss",
                    rejection_code=None if stressed_capped_qty > 0 else "ERR_GAP_STRESS_EXCEEDED",
                )

        return RiskValidationResult(
            is_approved=True,
            adjusted_quantity=proposed_quantity,
            reason="PRE_TRADE_PASSED: All boundary checks green",
        )
