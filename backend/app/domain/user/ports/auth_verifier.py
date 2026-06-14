from abc import ABC, abstractmethod
from typing import Dict, Any

class AuthVerifier(ABC):
    """
    Абстрактный интерфейс для проверки данных аутентификации.
    Реализация находится в infrastructure, но контракт живет в domain.
    """
    @abstractmethod
    def verify(self, init_data: str) -> Dict[str, Any]:
        pass