from typing import Optional, List
from abc import ABC, abstractmethod
from app.domain.order.entities.order import Order
from app.domain.user.value_objects.telegram_id import TelegramID


class OrderRepository(ABC):
    @abstractmethod
    async def find_by_telegram_id(self, telegram_id: TelegramID) -> List[Order]:
        pass

    @abstractmethod
    async def find_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    async def create(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def save(self, order: Order) -> Order:
        pass