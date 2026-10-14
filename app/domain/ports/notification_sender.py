from abc import ABC, abstractmethod
from app.domain.entities.customer import CustomerRef


class NotificationSender(ABC):
    @abstractmethod
    def send(self, customer: CustomerRef, restaurant_id: str, text: str) -> None:
        ...