import re
from app.domain.entities.conversation import Message
from app.domain.entities.menu import MenuItem
from app.domain.ports.order_parser import OrderParser, ParsedItem, ParsedOrder

CONFIRM_WORDS = {"تأكيد", "تاكيد", "اكد", "أكد", "confirm", "تمام", "ok", "اوك"}
MENU_WORDS = {"منيو", "المنيو", "القائمة", "menu"}
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

class SimpleOrderParser(OrderParser):

    def parse(self, message: str, menu: list[MenuItem], history: list[Message]) -> ParsedOrder:
        # 1. نضّف النص
        # 2. لو كلمة تأكيد: ارجع ParsedOrder(wants_checkout=True)
        # 3. لو كلمة منيو: ارجع ParsedOrder(wants_menu=True)
        # 4. لف على أصناف المنيو وابني قايمة ParsedItem
        # 5. ارجع ParsedOrder بالأصناف (أو فاضي لو ملقيتش حاجة)
        text = message.translate(ARABIC_DIGITS).strip().lower().strip("!.؟?")
        if text in CONFIRM_WORDS:
            return ParsedOrder(wants_checkout=True)

        if text in MENU_WORDS:
            return ParsedOrder(wants_menu=True)

        items: list[ParsedItem] = []
        for item in menu:
            name = item.name.lower()
            if name not in text:
                continue
            match = re.search(rf"(\d+)\s*{re.escape(name)}", text)
            quantity = int(match.group(1)) if match else 1

            size = next((s for s in item.sizes if s.lower() in text), None)

            items.append(ParsedItem(menu_item_id=item.id, quantity=quantity, size=size))

        return ParsedOrder(items=items)