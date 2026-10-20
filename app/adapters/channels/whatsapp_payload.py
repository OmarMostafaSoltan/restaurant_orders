"""Helpers that understand what Meta sends to our webhook (no web framework needed)."""
import hashlib
import hmac
from dataclasses import dataclass


@dataclass(frozen=True)
class IncomingText:
    phone_number_id: str    # the restaurant's number that received the message
    message_id: str         # wamid..., used to ignore duplicates
    sender: str             # the customer
    text: str


def signature_is_valid(raw_body: bytes, header: str, app_secret: str) -> bool:
    """header looks like: sha256=<hex digest of the raw body, signed with the app secret>"""
    if not app_secret or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def extract_text_messages(payload: dict) -> list[IncomingText]:
    """Only plain text messages. Delivery statuses, images, etc. are ignored."""
    found = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            phone_number_id = value.get("metadata", {}).get("phone_number_id", "")
            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue
                found.append(IncomingText(
                    phone_number_id=phone_number_id,
                    message_id=message.get("id", ""),
                    sender=message.get("from", ""),
                    text=message.get("text", {}).get("body", ""),
                ))
    return found