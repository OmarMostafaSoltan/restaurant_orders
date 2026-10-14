from decimal import Decimal

from app.adapters.parsers.simple_order_parser import SimpleOrderParser
from app.adapters.channels.consol_adapter import ConsoleNotificationSender
from app.adapters.websocket.console_puplisher import ConsolePublisher
from app.adapters.repositories.in_memory import (
    InMemoryConversationRepository,
    InMemoryMenuRepository,
    InMemoryOrderRepository,
)
from app.domain.entities.customer import CustomerRef
from app.domain.entities.menu import MenuItem
from app.domain.exceptions import DomainError
from app.use_cases.advance_order import AdvanceOrder
from app.use_cases.approve_order import ApproveOrder
from app.use_cases.get_kds_order import GetKdsOrders
from app.use_cases.process_customer_message import ProcessCustomerMessage
from app.use_cases.reject_order import RejectOrder

RESTAURANT_ID = "r1"

# ---------- 1. الـ repositories (بتتعمل مرة واحدة، عشان الذاكرة متتمسحش) ----------
menu_repo = InMemoryMenuRepository()
order_repo = InMemoryOrderRepository()
conversation_repo = InMemoryConversationRepository()

# ---------- 2. منيو تجريبي ----------
menu_repo.add(MenuItem(
    id="m_pizza", restaurant_id=RESTAURANT_ID, category_id="c_pizza",
    name="بيتزا", price=Decimal("100"),
    sizes={"صغيرة": Decimal("80"), "كبيرة": Decimal("120")},
))
menu_repo.add(MenuItem(
    id="m_cola", restaurant_id=RESTAURANT_ID, category_id="c_drinks",
    name="كولا", price=Decimal("15"),
))
menu_repo.add(MenuItem(
    id="m_burger", restaurant_id=RESTAURANT_ID, category_id="c_sandwich",
    name="برجر", price=Decimal("90"), is_available=False,   # مش متاح، عشان نجرب الرد
))

# ---------- 3. الـ adapters ----------
sender = ConsoleNotificationSender()
publisher = ConsolePublisher()
parser = SimpleOrderParser()

# ---------- 4. الـ use cases ----------
chat = ProcessCustomerMessage(menu_repo, order_repo, conversation_repo, parser, sender, publisher)
approve_order = ApproveOrder(order_repo, sender, publisher)
reject_order = RejectOrder(order_repo, sender, publisher)
advance_order = AdvanceOrder(order_repo, sender, publisher)
get_orders = GetKdsOrders(order_repo)

# ---------- 5. دوال مساعدة للشاشة ----------
HELP = """
اكتب رسالة العميل عادي: المنيو، 2 بيتزا كبيرة، كولا، تأكيد
أوامر الكاشير والمطبخ:
  /orders              اعرض الأوردرات النشطة
  /approve 1           وافق على الأوردر رقم 1 (من /orders)
  /reject 1 السبب      ارفض الأوردر
  /next 1              حرّك الأوردر (تحضير ثم جاهز)
  /as 99               اتكلم كعميل تاني (id = 99)
  /q                   خروج
"""


def show_orders():
    orders = get_orders.execute(RESTAURANT_ID)
    if not orders:
        print("(مفيش أوردرات نشطة)")
    for number, order in enumerate(orders, 1):
        items = ", ".join(f"{i.quantity}×{i.name}" for i in order.items)
        print(f"{number}. #{order.short_id} {order.status.value} | {items} | {order.total:.2f}")


def pick_order(number: str):
    orders = get_orders.execute(RESTAURANT_ID)
    try:
        return orders[int(number) - 1]
    except (ValueError, IndexError):
        print("رقم الأوردر غلط، اكتب /orders وشوف الأرقام")
        return None


def run_command(line: str, customer: CustomerRef) -> CustomerRef:
    parts = line.split(maxsplit=2)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    if command == "/orders":
        show_orders()
    elif command == "/as":
        customer = CustomerRef("dev", argument)
        print(f"(دلوقتي بتتكلم كعميل {argument})")
    elif command in ("/approve", "/next", "/reject"):
        order = pick_order(argument)
        if order is None:
            return customer
        if command == "/approve":
            approve_order.execute(RESTAURANT_ID, order.id)
        elif command == "/next":
            advance_order.execute(RESTAURANT_ID, order.id)
        else:
            reason = parts[2] if len(parts) > 2 else "غير محدد"
            reject_order.execute(RESTAURANT_ID, order.id, reason)
    else:
        print("أمر غير معروف")
    return customer


# ---------- 6. الحلقة ----------
def main():
    customer = CustomerRef("dev", "55")
    print(HELP)
    while True:
        line = input(">> ").strip()
        if not line:
            continue
        if line == "/q":
            break
        try:
            if line.startswith("/"):
                customer = run_command(line, customer)
            else:
                chat.execute(RESTAURANT_ID, customer, line)
        except DomainError as error:      # مثلاً InvalidOrderState
            print(f"(خطأ: {error})")


if __name__ == "__main__":
    main()