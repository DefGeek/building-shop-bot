from dataclasses import dataclass


@dataclass
class OrderItem:
    id: int | None
    order_id: int | None
    product_id: int
    product_name: str
    quantity: int
    price: float