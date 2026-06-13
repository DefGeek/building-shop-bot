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
from app.application.auth.commands.authenticate_user import AuthenticateUserHandler

_auth_verifier = TelegramAuthVerifier()
_token_generator = JwtTokenGenerator()
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
    """
    # 🔍 ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ для отладки
    print("=" * 50)
    print("🔍 [AUTH] Попытка декодирования токена")
    print(f"🔍 [AUTH] SECRET_KEY из settings: {settings.SECRET_KEY}")
    print(f"🔍 [AUTH] Длина SECRET_KEY: {len(settings.SECRET_KEY)}")
    
    token = credentials.credentials
    print(f"🔍 [AUTH] Получен токен: {token[:30]}...")
    
    try:
        # Сначала декодируем БЕЗ проверки подписи, чтобы увидеть, что внутри
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        print(f"🔍 [AUTH] Payload токена (без проверки): {unverified_payload}")
        
        # Теперь с проверкой подписи
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print(f"✅ [AUTH] Токен успешно декодирован!")
        
        telegram_id = payload.get("telegram_id")
        print(f"✅ [AUTH] Telegram ID из токена: {telegram_id}")
        print("=" * 50)

        if telegram_id is None:
            print("❌ [AUTH] telegram_id отсутствует в payload!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен: отсутствует telegram_id"
            )
        return int(telegram_id)
        
    except jwt.ExpiredSignatureError:
        print("❌ [AUTH] ОШИБКА: Токен просрочен!")
        print("=" * 50)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен просрочен"
        )
    except jwt.InvalidSignatureError as e:
        print(f"❌ [AUTH] ОШИБКА: Неверная подпись! {e}")
        print(f"❌ [AUTH] Возможно, SECRET_KEY изменился после выдачи токена")
        print("=" * 50)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная подпись токена"
        )
    except jwt.PyJWTError as e:
        print(f"❌ [AUTH] ОШИБКА JWT: {type(e).__name__}: {e}")
        print("=" * 50)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Невалидный токен: {str(e)}"
        )
    except Exception as e:
        print(f"❌ [AUTH] НЕОЖИДАННАЯ ОШИБКА: {type(e).__name__}: {e}")
        print("=" * 50)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка проверки токена: {str(e)}"
        )