from dataclasses import dataclass
from datetime import datetime

from app.domain.wallet.ports.wallet_repository import WalletRepository
from app.domain.user.value_objects.telegram_id import TelegramID


@dataclass
class GetWalletBalanceQuery:
    telegram_id: int


@dataclass
class WalletBalanceResponse:
    telegram_id: int
    balance: float
    created_at: datetime
    updated_at: datetime


class GetWalletBalanceHandler:
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository

    async def execute(self, query: GetWalletBalanceQuery) -> WalletBalanceResponse:
        telegram_id = TelegramID(query.telegram_id)
        wallet = await self.wallet_repository.find_by_telegram_id(telegram_id)

        # Если кошелька нет — создаем с нулевым балансом
        if not wallet:
            from app.domain.wallet.entities.wallet import Wallet
            from uuid import uuid4
            wallet = Wallet(
                id=uuid4(),
                telegram_id=telegram_id,
                balance=0.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            wallet = await self.wallet_repository.save(wallet)

        return WalletBalanceResponse(
            telegram_id=wallet.telegram_id.value,
            balance=wallet.balance,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
        )