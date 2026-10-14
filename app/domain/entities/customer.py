from dataclasses import dataclass

@dataclass(frozen=True)
class CustomerRef:
    channel: str        # "whatsapp" or "telegram"
    external_id: str    # phone number or chat id