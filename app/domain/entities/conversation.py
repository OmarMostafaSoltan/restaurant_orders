from dataclasses import dataclass, field

from app.domain.entities.customer import CustomerRef
from app.domain.entities.order import Order, OrderItem
from app.domain.exceptions import EmptyOrder


@dataclass
class Message:
    role: str     # "customer" or "bot"
    text: str


@dataclass
class Conversation:
    id: str
    restaurant_id: str
    customer: CustomerRef
    history: list[Message] = field(default_factory=list)
    cart: list[OrderItem] = field(default_factory=list)

    def add_message(self, role: str, text: str):
        self.history.append(Message(role, text))

    def add_to_cart(self, item: OrderItem):
        self.cart.append(item)

    def clear_cart(self):
        self.cart.clear()

    def checkout(self, order_id: str) -> Order:
        if not self.cart:
            raise EmptyOrder("cart is empty")
        order = Order(
            id=order_id,
            restaurant_id=self.restaurant_id,
            customer=self.customer,
            items=list(self.cart),
        )
        self.clear_cart()
        return order