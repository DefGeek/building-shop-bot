"""
application как и infrastructure импортирую только из domain
логика такая:
если смотреть почему application использует domain тот тут
вопросов нет - просто реализация поведения объектов

в application потом будет передаваться в presentation реализация
из infrastructure, и соответственно в infrastructure функции будут подаваться
domain объекты и поэтому они там тоже нужны (мапингом этот вопрос решается внутри)

также в infrastructure будет использоваться domain как базовый класс ABC для реализации
"""
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
        # Проверяется криптографическая подпись, которую серверы Telegram добавляют
        # к строке init_data при открытии Mini App
        #
        # т.е. серверы telegram берут данные юзера (id и тд) и токен бота и делают по ним хеш
        # и отпрпавляют на фронтенд, злоумышленник видит ДАННЫЕ+ХЕШ ОТ СЕРВЕРОВв
        # Злоумышленник может поменять данные,но не видит токен бота и поэтому
        # хеш посчитать правильно он не может и отрпавляет на бэкенд
        # бэкенд достаёт из базы данные,берёт токен и еслии на фронте
        # злоумышленние ничего не менял, то это действительно тот юзер который
        # за себя выдаёт
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