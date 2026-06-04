# app/di.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.telegram.auth_verifier import TelegramAuthVerifier

# Импорт из application
from application.auth.commands.authenticate_user import AuthenticateUserHandler

# Создаем синглтон верификатора (он не зависит от состояния конкретного запроса)
_auth_verifier = TelegramAuthVerifier()


def get_auth_handler(db: AsyncSession = Depends(get_db)) -> AuthenticateUserHandler:
    """
    Фабрика для создания хендлера.
    FastAPI автоматически вызовет эту функцию и внедрит зависимости.
    """
    # 1. Создаем инфраструктурную реализацию
    repo = UserRepositoryImpl(db)

    # 2. Собираем Use Case, передавая ему абстракции
    return AuthenticateUserHandler(
        user_repository=repo,
        auth_verifier=_auth_verifier
    )