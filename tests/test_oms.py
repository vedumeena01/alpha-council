"""
Unit Tests for Idempotent OMS and 1-Second Broker-Side GTT/SL-M Quantity Synchronization.
"""

from alphacouncil.execution.oms import IdempotentOMS, OrderStatus


def test_oms_bracket_entry_and_partial_fill_sync():
    oms = IdempotentOMS()

    # Create bracket entry: 1000 shares of RELIANCE
    entry_ord, stop_ord = oms.create_bracket_entry(
        symbol="RELIANCE",
        quantity=1000,
        entry_price=2500.0,
        stop_price=2450.0,
        target_price=2600.0,
    )

    assert entry_ord.symbol == "RELIANCE"
    assert entry_ord.quantity == 1000
    assert entry_ord.status == OrderStatus.SUBMITTED
    assert stop_ord.trigger_price == 2450.0
    assert stop_ord.quantity == 1000

    # Partial fill of 450 shares
    synced_stop = oms.record_partial_fill(
        entry_order_id=entry_ord.order_id,
        filled_shares=450,
        fill_price=2500.0,
    )

    assert synced_stop is not None
    assert synced_stop.quantity == 450  # Linked stop synchronized to 450 shares!
    assert entry_ord.status == OrderStatus.PARTIALLY_FILLED
    assert entry_ord.filled_quantity == 450
    assert oms.positions["RELIANCE"].shares == 450

    # Remaining 550 shares filled
    synced_stop_2 = oms.record_partial_fill(
        entry_order_id=entry_ord.order_id,
        filled_shares=550,
        fill_price=2501.0,
    )
    assert synced_stop_2 is not None
    assert synced_stop_2.quantity == 1000
    assert entry_ord.status == OrderStatus.FILLED
    assert oms.positions["RELIANCE"].shares == 1000


def test_oms_cancel_entry_and_orphaned_stops():
    oms = IdempotentOMS()

    entry_ord, stop_ord = oms.create_bracket_entry(
        symbol="TCS",
        quantity=500,
        entry_price=3500.0,
        stop_price=3430.0,
        target_price=3640.0,
    )

    assert entry_ord.status == OrderStatus.SUBMITTED
    assert stop_ord.status == OrderStatus.ACCEPTED

    # Cancel entry order before fill -> linked stop must be canceled as well
    res = oms.cancel_entry_and_orphaned_stops(entry_ord.order_id)
    assert res is True
    assert entry_ord.status == OrderStatus.CANCELED
    assert stop_ord.status == OrderStatus.CANCELED
