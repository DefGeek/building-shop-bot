from abc import ABC, abstractmethod
from uuid import UUID

class TokenGenerator(ABC):
    @abstractmethod
    def generate(self, user_id: UUID) -> str:
        pass