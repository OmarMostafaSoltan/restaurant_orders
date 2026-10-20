from pydantic import BaseModel

from app.domain.entities.order import Order


# ---------- شكل الطلبات الداخلة ----------
class DevMessage(BaseModel):
    customer_id: str = 201021333428
    text:str = "المنيو"
    channel: str = "whatsapp"


class RejectBody(BaseModel):
    reason: str


# ---------- شكل الردود الخارجة ----------
def order_to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "short_id": order.short_id,
        "status": order.status.value,
        "customer": {"channel": order.customer.channel, "id": order.customer.external_id},
        "items": [
            {
                "name": item.name,
                "quantity": item.quantity,
                "size": item.size,
                "notes": item.notes,
                "unit_price": str(item.unit_price),
                "total": str(item.total),
            }
            for item in order.items
        ],
        "total": str(order.total),
        "rejection_reason": order.rejection_reason,
        "created_at": order.created_at.isoformat(),
    }