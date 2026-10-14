from abc import ABC, abstractmethod

from app.domain.entities.order import Order


class OrderEventPublisher(ABC):
    @abstractmethod
    def publish(self,restaurant_id: str, order: Order, event: str) -> None:
        ...
