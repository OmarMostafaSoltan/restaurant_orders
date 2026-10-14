from app.domain.entities.order import Order
from app.domain.ports.order_repository import OrderRepository


class GetKdsOrders:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    def execute(self, restaurant_id: str) -> list[Order]:
        return self.order_repo.list_active(restaurant_id)