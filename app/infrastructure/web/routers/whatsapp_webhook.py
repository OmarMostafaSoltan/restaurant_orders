import hmac
import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.adapters.channels.whatsapp_payload import extract_text_messages, signature_is_valid
from app.domain.entities.customer import CustomerRef
from app.infrastructure.config.settings import settings
from app.infrastructure.web.dependencies import get_process_customer_message, get_restaurant_id
from app.use_cases.process_customer_message import ProcessCustomerMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp")

_seen_message_ids: set[str] = set()   # Meta may deliver the same message more than once


@router.get("")
def verify_webhook(
    mode: str = Query("", alias="hub.mode"),
    verify_token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    expected = settings.whatsapp_verify_token
    if mode == "subscribe" and expected and hmac.compare_digest(verify_token.encode(), expected.encode()):
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="verification failed")


def handle_message(use_case: ProcessCustomerMessage, restaurant_id: str, sender: str, text: str) -> None:
    customer = CustomerRef(channel="whatsapp", external_id=sender)   # القناة بتتحدد هنا
    try:
        use_case.execute(restaurant_id, customer, text)
    except Exception:
        logger.exception("failed to process WhatsApp message from %s", sender)


@router.post("")
async def receive_message(
    request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Depends(get_restaurant_id),
    use_case: ProcessCustomerMessage = Depends(get_process_customer_message),
):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature_is_valid(raw_body, signature, settings.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="invalid json")

    for incoming in extract_text_messages(payload):
        if incoming.phone_number_id != settings.whatsapp_phone_number_id:
            continue                      # رسالة على رقم مش بتاعنا
        if incoming.message_id in _seen_message_ids:
            continue                      # رسالة مكررة
        _seen_message_ids.add(incoming.message_id)
        background_tasks.add_task(handle_message, use_case, restaurant_id, incoming.sender, incoming.text)

    return {"status": "ok"}