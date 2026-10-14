from dataclasses import dataclass, field
from decimal import Decimal

@dataclass
class Category:
    id: str
    restaurant_id: str
    name: str

@dataclass
class MenuItem:
    id: str
    restaurant_id: str
    category_id: str
    name: str
    price: Decimal                                   # base price
    sizes: dict[str, Decimal] = field(default_factory=dict)   # {"large": Decimal("120")}
    is_available: bool = True

    def price_for(self, size: str | None) -> Decimal:
        if size and size in self.sizes:
            return self.sizes[size]
        return self.price