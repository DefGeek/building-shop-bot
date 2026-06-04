# presentation/api/auth_router.py (пример)
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db  # Ваша функция получения сессии БД
from domain.user.ports.auth_verifier import AuthVerifier
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.telegram.auth_verifier import TelegramAuthVerifier
from application.auth.commands.authenticate_user import (
    AuthenticateUserCommand,
    AuthenticateUserHandler
)

router = APIRouter()

# Создаем конкретные реализации (в реальном проекте это делает DI-контейнер, например, dependency-injector)
auth_verifier: AuthVerifier = TelegramAuthVerifier()


@router.post("/auth/telegram")
async def auth_telegram(
        x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
        db: AsyncSession = Depends(get_db)  # Получаем сессию БД
):
    try:
        # 1. Собираем зависимости
        user_repository = UserRepositoryImpl(db)
        handler = AuthenticateUserHandler(
            user_repository=user_repository,
            auth_verifier=auth_verifier
        )

        # 2. Создаем команду
        command = AuthenticateUserCommand(init_data=x_telegram_init_data)

        # 3. Выполняем сценарий
        response = await handler.execute(command)

        # 4. Возвращаем результат (FastAPI автоматически сериализует dataclass в JSON)
        return response

    except ValueError as e:
        # Ловим ошибки валидации от TelegramAuthVerifier
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # Ловим остальные ошибки БД и т.д.
        raise HTTPException(status_code=500, detail="Internal server error")