from abc import ABC, abstractmethod
from typing import Optional
from app.domain.wallet.entities.transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        pass

    @abstractmethod
    async def find_by_external_id(self, external_id: str) -> Optional[Transaction]:
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        pass