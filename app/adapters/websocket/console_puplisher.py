from app.domain.entities.order import Order
from app.domain.ports.order_event_publisher import OrderEventPublisher


class ConsolePublisher(OrderEventPublisher):
    def publish(self, restaurant_id: str, order: Order, event: str) -> None:
        # اطبع الحدث ورقم الأوردر وحالته
        print(f"[EVENT {restaurant_id}] {event} #{order.short_id} {order.status.value}")