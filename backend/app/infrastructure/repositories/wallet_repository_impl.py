from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.wallet.ports.wallet_repository import WalletRepository
from app.domain.wallet.entities.wallet import Wallet
from app.domain.user.value_objects.telegram_id import TelegramID
from app.infrastructure.database.models.wallet_model import WalletModel


class WalletRepositoryImpl(WalletRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, db_model: WalletModel) -> Wallet:
        """Преобразует модель БД в доменную сущность"""
        return Wallet(
            id=db_model.id,
            telegram_id=TelegramID(db_model.telegram_id),
            balance=db_model.balance,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

    def _to_db_model(self, domain_wallet: Wallet) -> WalletModel:
        """Преобразует доменную сущность в модель БД"""
        return WalletModel(
            id=domain_wallet.id,
            telegram_id=domain_wallet.telegram_id.value,
            balance=domain_wallet.balance,
            created_at=domain_wallet.created_at,
            updated_at=domain_wallet.updated_at,
        )

    async def find_by_telegram_id(self, telegram_id: TelegramID) -> Optional[Wallet]:
        """Найти кошелек по telegram_id"""
        result = await self.db.execute(
            select(WalletModel).where(WalletModel.telegram_id == telegram_id.value)
        )
        db_wallet = result.scalar_one_or_none()
        return self._to_domain(db_wallet) if db_wallet else None

    async def save(self, wallet: Wallet) -> Wallet:
        """Сохранить кошелек (update или insert)"""
        db_model = self._to_db_model(wallet)
        merged_model = await self.db.merge(db_model)
        await self.db.commit()
        await self.db.refresh(merged_model)
        return self._to_domain(merged_model)