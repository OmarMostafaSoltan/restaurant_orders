from abc import ABC, abstractmethod

from app.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def get_by_id(self, order_id: str, restaurant_id: str) -> Order|None:
        ...

    @abstractmethod
    def list_active(self, restaurant_id: str) -> list[Order]:
        ...