from abc import ABC, abstractmethod

class TokenVerifier(ABC):
    @abstractmethod
    def verify(self, token: str) -> int:
        """
        Проверяет токен и возвращает telegram_id.
        Если токен невалиден, должен выбросить исключение.
        """
        pass