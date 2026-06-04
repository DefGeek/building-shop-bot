from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.user.ports.user_repository import UserRepository
from app.domain.user.entities.user import User
from app.domain.user.value_objects.telegram_id import TelegramID

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_telegram_id(self, telegram_id: TelegramID):
        pass

    async def save(self, user: User):
        # Пока упрощённо, позже добавим полноценный mapper
        pass