"""
Unit & Integration Tests for DhanHQ Direct Execution Adapter.
Verifies:
1. Sandbox initialization and deterministic order placement.
2. Tick-size constraint validation and automatic tick-snapping to ₹0.05.
3. Fail-closed production mode enforcement (rejecting empty credentials).
4. Native GTT OCO bracket parameters (target, stop-loss, validity).
5. Position reconciliation, idempotency guard, and emergency circuit cancellation.
"""

import pytest
from alphacouncil.execution.dhan_adapter import (
    DhanExecutionAdapter,
    DhanProductType,
    NSE_SECURITY_ID_MAP,
    snap_to_nse_tick,
    is_valid_nse_tick,
)


def test_dhan_adapter_sandbox_order_placement():
    adapter = DhanExecutionAdapter(sandbox_mode=True)
    res = adapter.place_gtt_oco_bracket(
        symbol="RELIANCE",
        quantity=25,
        entry_price=1345.00,
        target_price=1370.00,
        stop_loss_price=1320.00,
        product_type=DhanProductType.CNC,
    )

    assert res.success is True
    assert res.order_id is not None
    assert res.order_id.startswith("DHAN-SIM-")
    assert res.order_status == "GTT_TRIGGER_PLACED"
    assert len(adapter.active_gtt_orders) == 1


def test_dhan_adapter_auto_snap_ticks():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    # Prices with non-tick decimals: 1345.03 -> 1345.05, 1370.08 -> 1370.10, 1320.02 -> 1320.00
    res = adapter.place_gtt_oco_bracket(
        symbol="RELIANCE",
        quantity=10,
        entry_price=1345.03,
        target_price=1370.08,
        stop_loss_price=1320.02,
        auto_snap_ticks=True,
    )

    assert res.success is True
    assert res.order_id is not None
    order = adapter.active_gtt_orders[res.order_id]
    assert order.entry_price == 1345.05
    assert order.target_price == 1370.10
    assert order.stop_loss_price == 1320.00
    assert is_valid_nse_tick(order.entry_trigger_price)
    assert is_valid_nse_tick(order.target_trigger_price)
    assert is_valid_nse_tick(order.stop_loss_trigger_price)


def test_dhan_adapter_tick_size_validation_rejects_when_snap_disabled():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    # When auto_snap_ticks=False, invalid tick must be gracefully rejected
    res = adapter.place_gtt_oco_bracket(
        symbol="RELIANCE",
        quantity=10,
        entry_price=1345.03,
        target_price=1370.00,
        stop_loss_price=1320.00,
        auto_snap_ticks=False,
    )

    assert res.success is False
    assert res.order_status == "REJECTED_TICK_SIZE"
    assert "Dhan requires prices in multiples of ₹0.05" in res.message


def test_dhan_adapter_invalid_quantity():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    res = adapter.place_gtt_oco_bracket(
        symbol="INFY",
        quantity=0,
        entry_price=1090.00,
        target_price=1120.00,
        stop_loss_price=1070.00,
    )
    assert res.success is False
    assert res.order_status == "REJECTED_ZERO_QUANTITY"


def test_dhan_adapter_unknown_symbol():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    res = adapter.place_gtt_oco_bracket(
        symbol="UNKNOWNSYM",
        quantity=10,
        entry_price=100.00,
        target_price=110.00,
        stop_loss_price=90.00,
    )
    assert res.success is False
    assert res.order_status == "REJECTED_UNKNOWN_SYMBOL"


def test_dhan_adapter_invalid_geometry():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    # Target lower than entry
    res1 = adapter.place_gtt_oco_bracket("TCS", 10, 2400.00, 2300.00, 2350.00)
    assert res1.success is False
    assert res1.order_status == "REJECTED_INVALID_GEOMETRY"

    # Stop higher than entry
    res2 = adapter.place_gtt_oco_bracket("TCS", 10, 2400.00, 2500.00, 2450.00)
    assert res2.success is False
    assert res2.order_status == "REJECTED_INVALID_GEOMETRY"


def test_dhan_adapter_idempotency_duplicate_protection():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    res1 = adapter.place_gtt_oco_bracket("SBIN", 50, 1170.00, 1200.00, 1150.00, allow_duplicate_symbol=False)
    assert res1.success is True

    # Attempting duplicate on same symbol
    res2 = adapter.place_gtt_oco_bracket("SBIN", 50, 1170.00, 1200.00, 1150.00, allow_duplicate_symbol=False)
    assert res2.success is False
    assert res2.order_status == "REJECTED_DUPLICATE_ORDER"


def test_dhan_adapter_production_mode_fails_without_credentials():
    with pytest.raises(ValueError, match="Production DhanExecutionAdapter requires valid DHAN_CLIENT_ID"):
        DhanExecutionAdapter(client_id="", access_token="", sandbox_mode=False)


def test_dhan_adapter_reconciliation_and_emergency_cancel():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    adapter.place_gtt_oco_bracket("TCS", 5, 2380.00, 2450.00, 2340.00)
    adapter.place_gtt_oco_bracket("SBIN", 50, 1170.00, 1200.00, 1150.00)

    assert len(adapter.active_gtt_orders) == 2

    audit = adapter.reconcile_positions()
    assert audit["status"] == "RECONCILED"
    assert audit["active_gtt_count"] == 2

    cancelled = adapter.emergency_cancel_all_gtt()
    assert cancelled == 2
    assert len(adapter.active_gtt_orders) == 0


def test_dhan_adapter_security_id_mapping():
    adapter = DhanExecutionAdapter(sandbox_mode=True)
    assert adapter.resolve_security_id("RELIANCE") == NSE_SECURITY_ID_MAP["RELIANCE"]
    assert adapter.resolve_security_id("HDFCBANK.NS") == NSE_SECURITY_ID_MAP["HDFCBANK"]
    assert snap_to_nse_tick(1452.33) == 1452.35
    assert snap_to_nse_tick(1452.32) == 1452.30
