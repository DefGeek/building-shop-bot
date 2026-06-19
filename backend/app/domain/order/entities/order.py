from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from app.domain.user.value_objects.telegram_id import TelegramID
from app.domain.order.entities.order_item import OrderItem


@dataclass
class Order:
    id: int | None
    telegram_id: TelegramID
    total_price: float
    customer_name: str
    phone: str
    address: str
    comment: str | None
    status: str
    payment_method: str
    created_at: datetime
    items: List[OrderItem] = field(default_factory=list)