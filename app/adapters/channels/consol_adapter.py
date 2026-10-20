from app.domain.entities.customer import CustomerRef
from app.domain.ports.notification_sender import NotificationSender


class ConsoleNotificationSender(NotificationSender):
    def send(self, customer: CustomerRef, restaurant_id: str,  text: str) -> None:
        # اطبع الرسالة بالشكل: [dev:55] نص الرسالة
        print(f"[{customer.channel}:{customer.external_id}] {text}")