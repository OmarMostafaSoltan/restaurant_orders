from uuid import uuid4

from app.domain.entities.conversation import Conversation
from app.domain.entities.customer import CustomerRef
from app.domain.entities.menu import MenuItem
from app.domain.entities.order import Order
from app.domain.ports.conversation_repository import ConversationRepository
from app.domain.ports.menu_repository import MenuRepository
from app.domain.ports.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders : dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._orders[order.id] = order 

    def get_by_id(self, order_id: str, restaurant_id: str) -> Order|None:
        order = self._orders.get(order_id)
        if order is None or order.restaurant_id != restaurant_id:
            return None
        return order

    def list_active(self, restaurant_id: str) -> list[Order]:
        orders = [
            order for order in self._orders.values()
            if order.restaurant_id == restaurant_id and order.is_active
        ]
        return sorted(orders, key=lambda order: order.created_at)    


class InMemoryMenuRepository(MenuRepository):
    def __init__(self):
        self._menus: dict[str, dict[str, MenuItem]] = {}

    def add(self, item: MenuItem) -> None:
        self._menus.setdefault(item.restaurant_id, {})[item.id] = item   #  للتجربة

    def get_menu(self, restaurant_id: str) -> list[MenuItem]:
        return list(self._menus.get(restaurant_id, {}).values())

    def get_item(self, restaurant_id: str, menu_item_id: str) -> MenuItem | None:
        return self._menus.get(restaurant_id, {}).get(menu_item_id)



class InMemoryConversationRepository(ConversationRepository):
    def __init__(self):
        self._conversations: dict[tuple[str, CustomerRef], Conversation] = {}

    def get_or_create(self, restaurant_id: str, customer: CustomerRef) -> Conversation:
        key = (restaurant_id, customer)
        if key not in self._conversations:
            self._conversations[key] = Conversation(
                id=uuid4().hex[:12],
                restaurant_id=restaurant_id,
                customer=customer,
            )
        return self._conversations[key]

    def save(self, conversation: Conversation) -> None:
        key = (conversation.restaurant_id, conversation.customer)
        self._conversations[key] = conversation