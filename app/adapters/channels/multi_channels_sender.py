import logging

from app.domain.entities.customer import CustomerRef
from app.domain.ports.notification_sender import NotificationSender

logger = logging.getLogger(__name__)


class MultiChannelSender(NotificationSender):
    """Sends the reply through the same channel the customer wrote from."""

    def __init__(self, senders: dict[str, NotificationSender]):
        self.senders = senders

    def send(self, customer: CustomerRef, restaurant_id: str,  text: str) -> None:
        sender = self.senders.get(customer.channel)
        if sender is None:
            logger.error("No sender configured for channel %r", customer.channel)
            return
        sender.send(customer, restaurant_id, text)