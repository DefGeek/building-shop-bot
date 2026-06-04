# application/auth/commands/authenticate_user.py
from dataclasses import dataclass

from app.domain.user.entities.user import User
from app.domain.user.ports.user_repository import UserRepository
from app.domain.user.value_objects.telegram_id import TelegramID
from app.domain.user.ports.auth_verifier import AuthVerifier  # <-- Только интерфейс!


@dataclass
class AuthenticateUserCommand:
    """Входные данные для сценария"""
    init_data: str


@dataclass
class AuthenticateUserResponse:
    """Выходные данные (DTO) сценария"""
    user_id: str
    telegram_id: int
    first_name: str
    full_name: str
    role: str
    is_new_user: bool


class AuthenticateUserHandler:
    def __init__(
            self,
            user_repository: UserRepository,
            auth_verifier: AuthVerifier  # <-- Внедряем через DI, а не создаем внутри
    ):
        self.user_repository = user_repository
        self.auth_verifier = auth_verifier

    async def execute(self, command: AuthenticateUserCommand) -> AuthenticateUserResponse:
        # 1. Проверка подписи (выбросит ValueError, если данные поддельные)
        telegram_data = self.auth_verifier.verify(command.init_data)

        # 2. Создание Value Object
        telegram_id = TelegramID(int(telegram_data['id']))

        # 3. Поиск или создание пользователя
        user = await self.user_repository.find_by_telegram_id(telegram_id)
        is_new_user = False

        if not user:
            user = User(
                telegram_id=telegram_id,
                first_name=telegram_data.get('first_name', ''),
                last_name=telegram_data.get('last_name'),
                username=telegram_data.get('username'),
            )
            is_new_user = True

        # 4. Обновление состояния и сохранение
        user.update_last_login()
        await self.user_repository.save(user)

        # 5. Возврат строго типизированного ответа
        return AuthenticateUserResponse(
            user_id=str(user.id),
            telegram_id=user.telegram_id.value,
            first_name=user.first_name,
            full_name=user.full_name,
            role=user.role.value,
            is_new_user=is_new_user
        )