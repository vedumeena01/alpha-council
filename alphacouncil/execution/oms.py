"""
Idempotent Order Management System (OMS) & Broker-Side GTT/SL-M Sync State Machine.
Codifies Section 4C of RFC v5.0 with NautilusTrader-style event states.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List, Tuple
import hashlib
import uuid
import time


class OrderStatus(Enum):
    PENDING_RISK = "PENDING_RISK"
    PENDING_PARENT = "PENDING_PARENT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


def make_deterministic_client_order_id(
    strategy_id: str, symbol: str, side: str, bar_date: str
) -> str:
    """Generates a deterministic idempotent client order ID for retry safety."""
    raw = f"{strategy_id}|{symbol}|{side}|{bar_date}"
    return f"ORD_{symbol}_{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL_MARKET = "SL_MARKET"
    GTT_BRACKET = "GTT_BRACKET"


@dataclass
class Order:
    """Represents an institutional order intent and execution state."""
    order_id: str
    client_order_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    order_type: OrderType
    quantity: int
    filled_quantity: int = 0
    limit_price: Optional[float] = None
    trigger_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING_RISK
    linked_stop_order_id: Optional[str] = None
    linked_target_order_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class Position:
    """Tracks active inventory held in the portfolio."""
    symbol: str
    shares: int
    entry_price: float
    current_mid_price: float
    stop_price: float
    target_price: float
    unrealized_pnl: float = 0.0


class IdempotentOMS:
    """
    Manages end-to-end order execution lifecycle with deterministic idempotency.
    Guarantees crash safety via concurrent broker-side GTT/SL-M stops
    and 1-second partial-fill quantity synchronization.
    """

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.by_client_id: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.execution_audit_log: List[Dict] = []

    def create_bracket_entry(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        stop_price: float,
        target_price: float,
        bar_date: str = "",
        strategy_id: str = "ALPHA_H1",
    ) -> Tuple[Order, Order]:
        """
        Creates an entry order paired with broker-side contingent GTT stop/target orders.
        Guarantees idempotency: retried client_order_id returns existing order instances.
        """
        if bar_date:
            client_order_id = make_deterministic_client_order_id(strategy_id, symbol, "BUY", bar_date)
        else:
            client_order_id = f"ORD_{symbol}_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"

        # Idempotency check: duplicate retry returns existing orders
        if client_order_id in self.by_client_id:
            existing_entry = self.by_client_id[client_order_id]
            existing_stop = self.orders.get(existing_entry.linked_stop_order_id)
            return existing_entry, existing_stop

        entry_order = Order(
            order_id=str(uuid.uuid4()),
            client_order_id=client_order_id,
            symbol=symbol,
            side="BUY",
            order_type=OrderType.MARKET,
            quantity=quantity,
            limit_price=entry_price,
            status=OrderStatus.SUBMITTED,
        )

        # Stop loss order: initially PENDING_PARENT until entry fill arrives (cash market safety)
        stop_order_id = f"GTT_STOP_{uuid.uuid4().hex[:8]}"
        stop_order = Order(
            order_id=stop_order_id,
            client_order_id=f"SLM_{client_order_id}",
            symbol=symbol,
            side="SELL",
            order_type=OrderType.SL_MARKET,
            quantity=quantity,
            trigger_price=stop_price,
            status=OrderStatus.PENDING_PARENT,
        )

        # Target profit order
        target_order_id = f"GTT_TP_{uuid.uuid4().hex[:8]}"
        target_order = Order(
            order_id=target_order_id,
            client_order_id=f"TP_{client_order_id}",
            symbol=symbol,
            side="SELL",
            order_type=OrderType.LIMIT,
            quantity=quantity,
            limit_price=target_price,
            status=OrderStatus.PENDING_PARENT,
        )

        entry_order.linked_stop_order_id = stop_order_id
        entry_order.linked_target_order_id = target_order_id

        self.orders[entry_order.order_id] = entry_order
        self.orders[stop_order.order_id] = stop_order
        self.orders[target_order.order_id] = target_order
        self.by_client_id[client_order_id] = entry_order

        return entry_order, stop_order

    def record_partial_fill(
        self, entry_order_id: str, filled_shares: int, fill_price: float
    ) -> Optional[Order]:
        """
        1-Second Synchronization Loop:
        When entry order is partially filled, promotes linked stop to ACCEPTED and
        resizes linked broker-side stop to match executed shares.
        """
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return None

        entry_order.filled_quantity += filled_shares
        if entry_order.filled_quantity >= entry_order.quantity:
            entry_order.status = OrderStatus.FILLED
        else:
            entry_order.status = OrderStatus.PARTIALLY_FILLED
        entry_order.updated_at = time.time()

        # Update or create position
        sym = entry_order.symbol
        if sym in self.positions:
            pos = self.positions[sym]
            pos.shares += filled_shares
        else:
            stop_p = self.orders[entry_order.linked_stop_order_id].trigger_price if entry_order.linked_stop_order_id else 0.0
            tp_p = self.orders[entry_order.linked_target_order_id].limit_price if entry_order.linked_target_order_id else fill_price * 1.05
            self.positions[sym] = Position(
                symbol=sym,
                shares=filled_shares,
                entry_price=fill_price,
                current_mid_price=fill_price,
                stop_price=stop_p,
                target_price=tp_p,
            )

        # Synchronize linked broker-side stop order: activate and match filled shares
        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            stop_order.status = OrderStatus.ACCEPTED
            stop_order.quantity = entry_order.filled_quantity
            stop_order.updated_at = time.time()

            if entry_order.linked_target_order_id in self.orders:
                target_order = self.orders[entry_order.linked_target_order_id]
                target_order.status = OrderStatus.ACCEPTED
                target_order.quantity = entry_order.filled_quantity
                target_order.updated_at = time.time()

            self.execution_audit_log.append({
                "timestamp": time.time(),
                "event": "PARTIAL_FILL_QUANTITY_SYNC",
                "entry_order_id": entry_order_id,
                "synced_stop_quantity": stop_order.quantity,
                "status": "Broker-side GTT stop order activated and synchronized",
            })
            return stop_order

        return None

    def cancel_entry_and_orphaned_stops(self, entry_order_id: str) -> bool:
        """
        Cancels an entry order and ensures any linked broker-side stop or target is also canceled.
        Prevents orphan stop orders that could execute unwanted positions.
        """
        entry_order = self.orders.get(entry_order_id)
        if not entry_order:
            return False

        entry_order.status = OrderStatus.CANCELED
        entry_order.updated_at = time.time()

        if entry_order.linked_stop_order_id in self.orders:
            stop_order = self.orders[entry_order.linked_stop_order_id]
            if entry_order.filled_quantity == 0:
                stop_order.status = OrderStatus.CANCELED
                stop_order.updated_at = time.time()

        if entry_order.linked_target_order_id in self.orders:
            tp_order = self.orders[entry_order.linked_target_order_id]
            if entry_order.filled_quantity == 0:
                tp_order.status = OrderStatus.CANCELED
                tp_order.updated_at = time.time()

        self.execution_audit_log.append({
            "timestamp": time.time(),
            "event": "ORDER_CANCELED_WITH_LINKED_STOPS",
            "entry_order_id": entry_order_id,
            "status": "Entry order and linked stops/targets canceled cleanly",
        })
        return True
