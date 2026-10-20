from decimal import Decimal
import secrets

from fastapi import Header, HTTPException

from app.adapters.channels.multi_channels_sender import MultiChannelSender
from app.adapters.channels.whatsapp_adapter import WhatsAppSender
from app.adapters.parsers.simple_order_parser import SimpleOrderParser
from app.adapters.channels.consol_adapter import ConsoleNotificationSender
from app.adapters.websocket.console_puplisher import ConsolePublisher
from app.adapters.repositories.in_memory import (
    InMemoryConversationRepository,
    InMemoryMenuRepository,
    InMemoryOrderRepository,
)
from app.domain.entities.menu import MenuItem
from app.infrastructure.config.settings import settings
from app.use_cases.advance_order import AdvanceOrder
from app.use_cases.approve_order import ApproveOrder
from app.use_cases.get_kds_order import GetKdsOrders
from app.use_cases.process_customer_message import ProcessCustomerMessage
from app.use_cases.reject_order import RejectOrder

# ---------- 1. كائنات طويلة العمر (مرة واحدة) ----------
# menu_repo, order_repo, conversation_repo, sender, publisher, parser
menu_repo = InMemoryMenuRepository()
order_repo = InMemoryOrderRepository()
conversation_repo = InMemoryConversationRepository()

sender = MultiChannelSender({
    "dev": ConsoleNotificationSender(),
    "whatsapp": WhatsAppSender(
        settings.whatsapp_token,
        settings.whatsapp_phone_number_id,
        settings.whatsapp_api_version,
    ),
})
publisher = ConsolePublisher()
parser = SimpleOrderParser()

# ---------- 2. منيو تجريبي ----------
menu_repo.add(MenuItem(
    id="m_pizza", restaurant_id=settings.default_restaurant_id, category_id="c_pizza",
    name="بيتزا", price=Decimal("100"),
    sizes={"صغيرة": Decimal("80"), "كبيرة": Decimal("120")},
))
menu_repo.add(MenuItem(
    id="m_cola", restaurant_id=settings.default_restaurant_id, category_id="c_drinks",
    name="كولا", price=Decimal("15"),
))
menu_repo.add(MenuItem(
    id="m_burger", restaurant_id=settings.default_restaurant_id, category_id="c_sandwich",
    name="برجر", price=Decimal("90"), is_available=False,   # مش متاح، عشان نجرب الرد
))


# ---------- 2. دوال بسيطة ----------
def get_restaurant_id() -> str:
    return settings.default_restaurant_id


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if not secrets.compare_digest(x_api_key.encode(), settings.api_key.encode()):
        raise HTTPException(status_code=401, detail="invalid api key")


# ---------- 3. الـ use cases ----------
def get_process_customer_message() -> ProcessCustomerMessage:
    return ProcessCustomerMessage(
        menu_repo, order_repo, conversation_repo, parser, sender, publisher
    )

# get_approve_order
def get_approve_order() -> ApproveOrder:
    return ApproveOrder(order_repo, sender, publisher)

# get_reject_order
def get_reject_order() -> RejectOrder:
    return RejectOrder(order_repo, sender, publisher)

# get_advance_order
def get_advance_order() -> AdvanceOrder:
    return AdvanceOrder(order_repo, sender, publisher)

# get_kds_orders
def get_kds_orders() -> GetKdsOrders:
    return GetKdsOrders(order_repo)