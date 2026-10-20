import logging
import httpx
from app.domain.entities.customer import CustomerRef
from app.domain.ports.notification_sender import NotificationSender

logger = logging.getLogger(__name__)


class WhatsAppSender(NotificationSender):
    def __init__(self, token: str, phone_number_id: str, api_version: str):
        self.token = token
        self.url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"

    def send(self, customer: CustomerRef, restaurant_id: str, text: str) -> None:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        body = {
            "messaging_product": "whatsapp",
            "to": customer.external_id,
            "type": "text",
            "text": {"body": text},
        }

        try:
            response = httpx.post(
                self.url,
                headers=headers,
                json=body,
                timeout=10.0,
            )
            if response.status_code >= 400:
                logger.error(
                    "WhatsApp API error for restaurant %s to %s: status=%s, body=%s",
                    restaurant_id,
                    customer.external_id,
                    response.status_code,
                    response.text,
                )
        except httpx.RequestError as exc:
            logger.error(
                "Network error while sending WhatsApp message to %s: %s",
                customer.external_id,
                exc,
            )