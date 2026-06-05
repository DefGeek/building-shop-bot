# app/infrastructure/repositories/user_repository_impl.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.user.ports.user_repository import UserRepository
from app.domain.user.entities.user import User
from app.domain.user.value_objects.telegram_id import TelegramID
from app.domain.user.value_objects.user_role import UserRole

# Импортируем только что созданную модель
from app.infrastructure.database.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, db_model: UserModel) -> User:
        """
        МАППИНГ
        Преобразует модель БД в доменную сущность
        """
        user = User(
            telegram_id=TelegramID(db_model.telegram_id),
            first_name=db_model.first_name,
            last_name=db_model.last_name,
            username=db_model.username,
        )
        user.id = db_model.id
        user.role = UserRole(db_model.role)
        user.is_active = db_model.is_active
        user.created_at = db_model.created_at
        user.last_login = db_model.last_login
        return user

    def _to_db_model(self, domain_user: User) -> UserModel:
        """
        МАППИНГ
        Преобразует доменную сущность в модель БД
        """
        return UserModel(
            id=domain_user.id,
            telegram_id=domain_user.telegram_id.value,
            first_name=domain_user.first_name,
            last_name=domain_user.last_name,
            username=domain_user.username,
            role=domain_user.role.value,
            is_active=domain_user.is_active,
            created_at=domain_user.created_at,
            last_login=domain_user.last_login,
        )

    async def find_by_telegram_id(self, telegram_id: TelegramID) -> Optional[User]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id.value)
        )
        db_user = result.scalar_one_or_none()
        return self._to_domain(db_user) if db_user else None

    async def save(self, user: User) -> User:
        db_model = self._to_db_model(user)
        #данная функция проверяет есть ли в базе запись с таким же id
        #если есть то делает её update
        #иначе делает её insert
        merged_model = await self.db.merge(db_model)
        await self.db.commit()
        #для надёжности проверяем обновлись ли данные в базе преджде
        #чем превратить их в доменную сущность
        await self.db.refresh(merged_model)
        #Обазаны вернуть доменную сущность согласно DDD
        return self._to_domain(merged_model)