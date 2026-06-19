from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from app.domain.user.value_objects.telegram_id import TelegramID


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Transaction:
    id: UUID
    telegram_id: TelegramID
    amount: float
    status: TransactionStatus
    external_payment_id: str | None
    created_at: datetime

    def mark_success(self):
        if self.status != TransactionStatus.PENDING:
            raise ValueError("Транзакция уже обработана")
        self.status = TransactionStatus.SUCCESS