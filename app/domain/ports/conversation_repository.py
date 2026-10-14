from abc import ABC, abstractmethod
from app.domain.entities.conversation import Conversation
from app.domain.entities.customer import CustomerRef


class ConversationRepository(ABC):
    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        ...

    @abstractmethod
    def get_or_create(self, customer: CustomerRef, restaurant_id: str) -> Conversation:
        ...