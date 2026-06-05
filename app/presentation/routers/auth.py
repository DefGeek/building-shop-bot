"""
auth.py получает сырой HTTP-запрос.
dependencies.py собирает конкретные реализации из infrastructure (сессию БД, верификатор).
Эти реализации "засовываются" внутрь объекта application (Handler).
Handler выполняет конкретное бизнес-поведение, вообще не зная, как и откуда взялись эти зависимости.
"""
from fastapi import APIRouter, Header, HTTPException, Depends

from app.application.auth.commands.authenticate_user import (
    AuthenticateUserCommand,
    AuthenticateUserHandler
)
from app.presentation.dependencies import get_auth_handler

router = APIRouter()

@router.post("/auth/telegram")
async def auth_telegram(
    x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
    #Соблюдаем Паттерн проектирования Dependency Injection при котором объект не создаёт
    #необходимые ему зависимости самостоятельно, а получает их извне
    handler: AuthenticateUserHandler = Depends(get_auth_handler)
):
    try:
        # 1. Presentation преобразует сырой HTTP-запрос в Команду
        command = AuthenticateUserCommand(init_data=x_telegram_init_data)

        # 2. Presentation передает управление в Application
        response = await handler.execute(command)

        # 3. Presentation возвращает ответ клиенту
        return response

    except ValueError as e:
        # Ловим бизнес-ошибки (например, "Invalid Telegram signature")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # Ловим непредвиденные ошибки
        raise HTTPException(status_code=500, detail="Internal server error")