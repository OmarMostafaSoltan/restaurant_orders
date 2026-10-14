from decimal import Decimal

from app.domain.entities.conversation import Conversation
from app.domain.entities.customer import CustomerRef
from app.domain.entities.menu import MenuItem
from app.domain.entities.order import OrderItem
from app.domain.exceptions import EmptyOrder, SizeNotAvailable
from app.domain.ports.conversation_repository import ConversationRepository
from app.domain.ports.menu_repository import MenuRepository
from app.domain.ports.notification_sender import NotificationSender
from app.domain.ports.order_event_publisher import OrderEventPublisher
from app.domain.ports.order_parser import OrderParser
from app.domain.ports.order_repository import OrderRepository
from uuid import uuid4

DEFAULT_REPLY = 'مفهمتش طلبك، اكتب "المنيو" عشان تشوف الأصناف.'


class ProcessCustomerMessage:
    def __init__(
        self,
        menu_repo: MenuRepository,
        order_repo: OrderRepository,
        conversation_repo: ConversationRepository,
        parser: OrderParser,
        sender: NotificationSender,
        publisher: OrderEventPublisher
    ):
        self.menu_repo = menu_repo
        self.order_repo = order_repo
        self.conversation_repo = conversation_repo
        self.parser = parser
        self.sender = sender
        self.publisher = publisher

    def execute(self, restaurant_id: str, customer: CustomerRef, text: str) -> str:
        conversation = self.conversation_repo.get_or_create(restaurant_id, customer)
        conversation.add_message("customer", text)
        menu = self.menu_repo.get_menu(restaurant_id)
        parsed = self.parser.parse(text, menu, conversation.history)
        lines: list[str] = []

        if parsed.wants_menu:
            lines.append(self._menu_text(menu))

        if parsed.clarification_question:
            lines.append(parsed.clarification_question)

        added_any = False
        for parsed_item in parsed.items:
            problem = self._add_to_cart(restaurant_id, conversation, parsed_item)
            if problem:
                lines.append(problem)
            else:
                added_any = True

        if added_any and not parsed.wants_checkout:
            lines.append(self._cart_text(conversation))

        if parsed.wants_checkout:
            lines.append(self._checkout(restaurant_id, conversation))

        if not lines:
            lines.append(DEFAULT_REPLY)

        reply = "\n".join(lines)
        conversation.add_message("bot", reply)
        self.conversation_repo.save(conversation)
        self.sender.send(restaurant_id, customer, reply)
        return reply


    def _add_to_cart(self, restaurant_id, conversation, parsed) -> str | None:
        item = self.menu_repo.get_item(restaurant_id, parsed.menu_item_id)
        if item is None or not item.is_available:
            name = item.name if item else "الصنف ده"
            return f"{name} مش متاح دلوقتي."

        try:
            unit_price = item.price_for(parsed.size)
        except SizeNotAvailable:
            return f'المقاس "{parsed.size}" مش متاح في {item.name}.'

        conversation.add_to_cart(OrderItem(
            menu_item_id=item.id, name=item.name, unit_price=unit_price,
            quantity=parsed.quantity, size=parsed.size, notes=parsed.notes,
        ))
        return None

    def _checkout(self, restaurant_id, conversation) -> str:
        try:
            order = conversation.checkout(uuid4().hex[:12])
        except EmptyOrder:
            return "السلة فاضية، اكتب اسم الصنف اللي عايزه الأول."

        self.order_repo.save(order)
        self.publisher.publish(restaurant_id, order, "order_created")
        return (
            f"تم استلام طلبك رقم {order.short_id}\n"
            f"الإجمالي: {order.total:.2f} جنيه\n"
            "في انتظار موافقة المطعم."
        )

    @staticmethod
    def _cart_text(conversation: Conversation) -> str:
        lines = ["سلتك:"]
        total = Decimal("0")
        for item in conversation.cart:
            size = f" ({item.size})" if item.size else ""
            lines.append(f"- {item.quantity} × {item.name}{size} = {item.total:.2f}")
            total += item.total
        lines.append(f"الإجمالي: {total:.2f} جنيه")
        lines.append('اكتب "تأكيد" لإرسال الطلب، أو كمّل اختيار أصناف.')
        return "\n".join(lines)

    @staticmethod
    def _menu_text(menu: list[MenuItem]) -> str:
        available = [m for m in menu if m.is_available]
        if not available:
            return "المنيو فاضي دلوقتي."
        lines = ["المنيو:"]
        for m in available:
            sizes = ""
            if m.sizes:
                sizes = " (" + " / ".join(f"{s} {p:.2f}" for s, p in m.sizes.items()) + ")"
            lines.append(f"- {m.name}: {m.price:.2f}{sizes}")
        return "\n".join(lines)