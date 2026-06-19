from typing import Optional
from abc import ABC, abstractmethod
from app.domain.wallet.entities.wallet import Wallet
from app.domain.user.value_objects.telegram_id import TelegramID


class WalletRepository(ABC):
    @abstractmethod
    async def find_by_telegram_id(self, telegram_id: TelegramID) -> Optional[Wallet]:
        pass

    @abstractmethod
    async def save(self, wallet: Wallet) -> Wallet:
        pass