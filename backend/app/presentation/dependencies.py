"""
Суть dependencies чтобы брать реализации из architecture
и передавать их в сценарии из application
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем из app.database (как в вашем tree)
from app.database import get_db
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.infrastructure.telegram.auth_verifier import TelegramAuthVerifier
from app.infrastructure.security.jwt import JwtTokenGenerator
from app.application.auth.commands.authenticate_user import AuthenticateUserHandler

# Синглтон верификатора
# Синглтон - паттерн проектирования, при котором класс имеет один единственный
# экземпляр на всё время работы приложения и все части программы
# используют именно этот один объект
_auth_verifier = TelegramAuthVerifier()
_token_generator = JwtTokenGenerator()


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
    Используется в защищенных роутах (например, создание заказа),
    чтобы знать, от какого пользователя пришел запрос.
    """
    try:
        # Декодируем токен, используя тот же SECRET_KEY, которым он был создан
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        telegram_id = payload.get("telegram_id")

        if telegram_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен: отсутствует telegram_id"
            )
        return int(telegram_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен"
        )