from app.domain.entities.order import Order, OrderStatus
from app.domain.exceptions import InvalidOrderState, OrderNotFound
from app.domain.ports.notification_sender import NotificationSender
from app.domain.ports.order_event_publisher import OrderEventPublisher
from app.domain.ports.order_repository import OrderRepository


class AdvanceOrder:
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
        order = self.order_repo.get_by_id(order_id, restaurant_id )
        if order is None:
            raise OrderNotFound(order_id)

        if order.status == OrderStatus.APPROVED:
            order.start_preparing()
            message = f"طلبك رقم {order.short_id} بدأ تحضيره."
        elif order.status == OrderStatus.PREPARING:
            order.mark_ready()
            message = f"طلبك رقم {order.short_id} جاهز."
        else:
            raise InvalidOrderState(f"cannot advance order in state {order.status.value}")

        self.order_repo.save(order)

        self.sender.send(restaurant_id, order.customer, message)
        self.publisher.publish(restaurant_id, order, "order_updated")
        return order