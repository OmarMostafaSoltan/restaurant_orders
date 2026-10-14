
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.domain.entities.conversation import Message
from app.domain.entities.menu import MenuItem


@dataclass
class ParsedItem:
    menu_item_id: str
    quantity: int
    size: str | None = None
    notes: str=""

@dataclass
class ParsedOrder:
    items: list[ParsedItem] = field(default_factory=list)
    wants_checkout: bool = False
    wants_menu: bool = False
    clarification_question: str | None = None

class OrderParser(ABC):
    @abstractmethod
    def parse(self, message: str, menu: list[MenuItem],history: list[Message]) -> ParsedOrder:
        ...