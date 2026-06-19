from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.domain.wallet.ports.wallet_repository import WalletRepository
from app.domain.wallet.ports.transaction_repository import TransactionRepository
from app.domain.wallet.ports.payment_gateway import PaymentGateway, PaymentRequest
from app.domain.wallet.entities.transaction import Transaction, TransactionStatus
from app.domain.user.value_objects.telegram_id import TelegramID


@dataclass
class TopUpWalletCommand:
    telegram_id: int
    amount: float


@dataclass
class TopUpWalletResponse:
    payment_id: str
    confirmation_url: str


class TopUpWalletHandler:
    def __init__(
        self,
        wallet_repo: WalletRepository,
        transaction_repo: TransactionRepository,
        payment_gateway: PaymentGateway
    ):
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo
        self.payment_gateway = payment_gateway

    async def execute(self, command: TopUpWalletCommand) -> TopUpWalletResponse:
        if command.amount <= 0:
            raise ValueError("Сумма пополнения должна быть больше 0")

        telegram_id = TelegramID(command.telegram_id)
        external_id = str(uuid4())

        # 1. Создаем транзакцию в статусе PENDING
        transaction = Transaction(
            id=uuid4(),
            telegram_id=telegram_id,
            amount=command.amount,
            status=TransactionStatus.PENDING,
            external_payment_id=None,
            created_at=datetime.utcnow()
        )
        transaction = await self.transaction_repo.create(transaction)

        # 2. Запрашиваем ссылку на оплату у платежного шлюза
        payment_request = PaymentRequest(
            amount=command.amount,
            description=f"Пополнение кошелька, транзакция {transaction.id}",
            external_id=str(transaction.id)
        )
        payment_response = await self.payment_gateway.create_payment(payment_request)

        # 3. Сохраняем ID платежа из шлюза
        transaction.external_payment_id = payment_response.external_payment_id
        await self.transaction_repo.save(transaction)

        return TopUpWalletResponse(
            payment_id=payment_response.external_payment_id,
            confirmation_url=payment_response.confirmation_url
        )