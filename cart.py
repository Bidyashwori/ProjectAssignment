from dataclasses import dataclass


@dataclass(frozen=True)
class CartContents:
    item_name: str
    quantity: int | None
    badge_count: int | None
