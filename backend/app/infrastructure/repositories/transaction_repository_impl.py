from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.wallet.ports.transaction_repository import TransactionRepository
from app.domain.wallet.entities.transaction import Transaction
from app.domain.user.value_objects.telegram_id import TelegramID
from app.infrastructure.database.models.transaction_model import TransactionModel

class TransactionRepositoryImpl(TransactionRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            telegram_id=TelegramID(model.telegram_id),
            amount=model.amount,
            status=model.status,
            external_payment_id=model.external_payment_id,
            created_at=model.created_at,
        )

    def _to_model(self, entity: Transaction) -> TransactionModel:
        return TransactionModel(
            id=entity.id,
            telegram_id=entity.telegram_id.value,
            amount=entity.amount,
            status=entity.status,
            external_payment_id=entity.external_payment_id,
            created_at=entity.created_at,
        )

    async def create(self, transaction: Transaction) -> Transaction:
        model = self._to_model(transaction)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def find_by_external_id(self, external_id: str) -> Optional[Transaction]:
        result = await self.db.execute(
            select(TransactionModel).where(TransactionModel.external_payment_id == external_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, transaction: Transaction) -> Transaction:
        model = self._to_model(transaction)
        merged = await self.db.merge(model)
        await self.db.commit()
        await self.db.refresh(merged)
        return self._to_domain(merged)