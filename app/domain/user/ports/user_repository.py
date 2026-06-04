from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.user.entities.user import User
from app.domain.user.value_objects.telegram_id import TelegramID

class UserRepository(ABC):

    @abstractmethod
    async def find_by_telegram_id(self, telegram_id: TelegramID) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass