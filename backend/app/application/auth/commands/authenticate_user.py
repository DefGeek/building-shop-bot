"""
application как и infrastructure импортирую только из domain
логика такая:
если смотреть почему application использует domain тот тут
вопросов нет - просто реализация поведения объектов

в application потом будет передаваться в presentation реализация
из infrastructure, и соответственно в infrastructure функции будут подаваться
domain объекты и поэтому они там тоже нужны (мапингом этот вопрос решается внутри)
"""
from dataclasses import dataclass
from sqlalchemy.exc import IntegrityError  # <-- ДОБАВИЛИ этот импорт для перехвата ошибки БД

from app.domain.user.entities.user import User
from app.domain.user.ports.user_repository import UserRepository
from app.domain.user.value_objects.telegram_id import TelegramID
from app.domain.user.ports.auth_verifier import AuthVerifier
from app.domain.user.ports.token_generator import TokenGenerator


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
    access_token: str


class AuthenticateUserHandler:
    def __init__(
            self,
            user_repository: UserRepository,
            auth_verifier: AuthVerifier,
            token_generator: TokenGenerator
    ):
        self.user_repository = user_repository
        self.auth_verifier = auth_verifier
        self.token_generator = token_generator

    async def execute(self, command: AuthenticateUserCommand) -> AuthenticateUserResponse:
        # 1. Проверка подписи
        telegram_data = self.auth_verifier.verify(command.init_data)

        # 2. Создание Value Object
        telegram_id = TelegramID(int(telegram_data['user']['id']))

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

            # 4. Попытка сохранения с защитой от гонки данных (Race Condition)
            # Это защита от эффекта React когда он может два раза отправить запрос на серсерв
            try:
                await self.user_repository.save(user)
            except IntegrityError:
                # Если здесь произошла ошибка, значит параллельный запрос
                # уже успел создать этого пользователя.
                # Мы просто находим его, не нарушая инкапсуляцию репозитория.
                user = await self.user_repository.find_by_telegram_id(telegram_id)
                is_new_user = False  # Сбрасываем флаг, так как пользователь уже был в БД

        # 5. Обновление состояния и сохранение (теперь user точно существует и валиден)
        user.update_last_login()
        await self.user_repository.save(user)

        # 6. Возврат строго типизированного ответа
        return AuthenticateUserResponse(
            user_id=str(user.id),
            telegram_id=user.telegram_id.value,
            first_name=user.first_name,
            full_name=user.full_name,
            role=user.role.value,
            is_new_user=is_new_user,
            access_token=self.token_generator.generate(user.id, user.telegram_id)
        )