from app.domain.entities.order import Order
from app.domain.exceptions import OrderNotFound
from app.domain.ports.notification_sender import NotificationSender
from app.domain.ports.order_event_publisher import OrderEventPublisher
from app.domain.ports.order_repository import OrderRepository


class ApproveOrder:
    def __init__(
        self,
        order_repo: OrderRepository,
        sender: NotificationSender,
        publisher: OrderEventPublisher,
    ):
        
        self.order_repo = order_repo
        self.sender = sender
        self.publisher = publisher

    def execute(self, restaurant_id: str, order_id: str) -> Order:
        order = self.order_repo.get_by_id(order_id,restaurant_id)
        if order is None:
            raise OrderNotFound(order_id)

        order.approve()
        self.order_repo.save(order)

        self.sender.send(restaurant_id, order.customer, f"تم قبول طلبك رقم {order.short_id}")
        self.publisher.publish(restaurant_id, order, "order_updated")
        return order
