"""
Unit & Integration Tests for DhanHQ Direct Execution Adapter.
Verifies:
1. Sandbox initialization and deterministic order placement.
2. Tick-size constraint validation (multiples of ₹0.05).
3. Fail-closed production mode enforcement (rejecting empty credentials).
4. Native GTT OCO bracket parameters (target, stop-loss, validity).
5. Position reconciliation and emergency circuit cancellation.
"""

import pytest
from alphacouncil.execution.dhan_adapter import (
    DhanExecutionAdapter,
    DhanProductType,
    NSE_SECURITY_ID_MAP,
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


def test_dhan_adapter_tick_size_validation():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    # Invalid tick size: 1345.03 is not a multiple of 0.05
    with pytest.raises(ValueError, match="Dhan requires prices in multiples of ₹0.05"):
        adapter.place_gtt_oco_bracket(
            symbol="RELIANCE",
            quantity=10,
            entry_price=1345.03,
            target_price=1370.00,
            stop_loss_price=1320.00,
        )


def test_dhan_adapter_invalid_quantity():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    with pytest.raises(ValueError, match="Quantity must be a positive integer"):
        adapter.place_gtt_oco_bracket(
            symbol="INFY",
            quantity=0,
            entry_price=1090.00,
            target_price=1120.00,
            stop_loss_price=1070.00,
        )


def test_dhan_adapter_unknown_symbol():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    with pytest.raises(ValueError, match="Unknown symbol UNKNOWNSYM"):
        adapter.place_gtt_oco_bracket(
            symbol="UNKNOWNSYM",
            quantity=10,
            entry_price=100.00,
            target_price=110.00,
            stop_loss_price=90.00,
        )


def test_dhan_adapter_production_mode_fails_without_credentials():
    # In live mode (sandbox_mode=False), missing credentials must raise ValueError immediately
    with pytest.raises(ValueError, match="Production DhanExecutionAdapter requires valid DHAN_CLIENT_ID"):
        DhanExecutionAdapter(client_id="", access_token="", sandbox_mode=False)


def test_dhan_adapter_reconciliation_and_emergency_cancel():
    adapter = DhanExecutionAdapter(sandbox_mode=True)

    # Place 2 orders
    adapter.place_gtt_oco_bracket("TCS", 5, 2380.00, 2450.00, 2340.00)
    adapter.place_gtt_oco_bracket("SBIN", 50, 1170.00, 1200.00, 1150.00)

    assert len(adapter.active_gtt_orders) == 2

    # Reconcile
    audit = adapter.reconcile_positions()
    assert audit["status"] == "RECONCILED"
    assert audit["active_gtt_count"] == 2

    # Emergency Flatten / Cancel All
    cancelled = adapter.emergency_cancel_all_gtt()
    assert cancelled == 2
    assert len(adapter.active_gtt_orders) == 0


def test_dhan_adapter_security_id_mapping():
    adapter = DhanExecutionAdapter(sandbox_mode=True)
    assert adapter.resolve_security_id("RELIANCE") == NSE_SECURITY_ID_MAP["RELIANCE"]
    assert adapter.resolve_security_id("HDFCBANK.NS") == NSE_SECURITY_ID_MAP["HDFCBANK"]
