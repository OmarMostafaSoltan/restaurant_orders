from dataclasses import dataclass

@dataclass
class Restaurant:
    id: str
    name: str
    currency: str = "EGP"
    timezone: str = "Africa/Cairo"
    is_active: bool = True