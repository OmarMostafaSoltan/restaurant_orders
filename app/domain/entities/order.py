from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from app.domain.entities.customer import CustomerRef
from app.domain.exceptions import InvalidOrderState


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PREPARING = "PREPARING"
    READY = "READY"
    REJECTED = "REJECTED"


ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.APPROVED, OrderStatus.REJECTED},
    OrderStatus.APPROVED: {OrderStatus.PREPARING},
    OrderStatus.PREPARING: {OrderStatus.READY},
    OrderStatus.READY: set(),
    OrderStatus.REJECTED: set(),
}


@dataclass
class OrderItem:
    menu_item_id: str
    name: str                 # copied from the menu at order time
    unit_price: Decimal       # copied too, menu prices may change later
    quantity: int = 1
    size: str | None = None
    notes: str = ""

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: str
    restaurant_id: str
    customer: CustomerRef
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    rejection_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def short_id(self) -> str:
        return self.id[:6].upper()
    
    @property
    def total(self) -> Decimal:
        return sum((i.total for i in self.items), Decimal("0"))
    
    @property
    def is_active(self) -> bool:
        return self.status in (OrderStatus.PENDING, OrderStatus.APPROVED, OrderStatus.PREPARING)
    
    def approve(self):
        self._move_to(OrderStatus.APPROVED)

    def reject(self, reason: str):
        self._move_to(OrderStatus.REJECTED)
        self.rejection_reason = reason

    def start_preparing(self):
        self._move_to(OrderStatus.PREPARING)

    def mark_ready(self):
        self._move_to(OrderStatus.READY)

    def _move_to(self, new_status: OrderStatus):
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidOrderState(
                f"cannot move order from {self.status.value} to {new_status.value}"
            )
        self.status = new_status