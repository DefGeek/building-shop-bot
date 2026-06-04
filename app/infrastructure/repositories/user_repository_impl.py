from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.user.repositories.user_repository import UserRepository
from domain.user.entities.user import User
from domain.user.value_objects.telegram_id import TelegramID
from app.models.user import User as UserModel   # SQLAlchemy модель

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_telegram_id(self, telegram_id: TelegramID):
        result = await self.db.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id.value)
        )
        db_user = result.scalar_one_or_none()
        # Здесь можно добавить mapper из db_model в domain entity при необходимости
        return db_user  # Пока упрощённо

    async def save(self, user: User):
        # Пока упрощённо, позже добавим полноценный mapper
        pass