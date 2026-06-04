# app/presentation/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем из app.database (как в вашем tree)
from app.database import get_db
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.telegram.auth_verifier import TelegramAuthVerifier
from app.application.auth.commands.authenticate_user import AuthenticateUserHandler

# Синглтон верификатора
_auth_verifier = TelegramAuthVerifier()


def get_auth_handler(db: AsyncSession = Depends(get_db)) -> AuthenticateUserHandler:
    """
    Фабрика для создания хендлера.
    """
    repo = UserRepositoryImpl(db)

    return AuthenticateUserHandler(
        user_repository=repo,
        auth_verifier=_auth_verifier
    )