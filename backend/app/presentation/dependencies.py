"""
Суть dependencies чтобы брать реализации из architecture
и передавать их в сценарии из application
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import settings
from app.database import get_db
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.telegram.auth_verifier import TelegramAuthVerifier
from app.infrastructure.security.jwt import JwtTokenGenerator
from app.infrastructure.security.jwt_verifier import JwtTokenVerifier
from app.application.auth.commands.authenticate_user import AuthenticateUserHandler

_auth_verifier = TelegramAuthVerifier()
_token_generator = JwtTokenGenerator()
_token_verifier = JwtTokenVerifier()
security = HTTPBearer()


def get_auth_handler(db: AsyncSession = Depends(get_db)) -> AuthenticateUserHandler:
    """
    Фабрика для создания хендлера.
    """
    repo = UserRepositoryImpl(db)
    return AuthenticateUserHandler(
        user_repository=repo,
        auth_verifier=_auth_verifier,
        token_generator=_token_generator
    )


def get_current_telegram_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Извлекает telegram_id из JWT токена.
    Теперь эта функция ТОЛЬКО делегирует работу инфраструктурному сервису.
    """
    return _token_verifier.verify(credentials.credentials)