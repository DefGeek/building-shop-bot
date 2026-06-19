from dataclasses import dataclass
from app.domain.wallet.ports.wallet_repository import WalletRepository
from app.domain.wallet.ports.transaction_repository import TransactionRepository
from app.domain.wallet.entities.transaction import TransactionStatus


@dataclass
class ProcessWebhookCommand:
    external_payment_id: str
    status: str  # 'succeeded' или 'canceled'
    amount: float


class ProcessPaymentWebhookHandler:
    def __init__(
            self,
            wallet_repo: WalletRepository,
            transaction_repo: TransactionRepository
    ):
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo

    async def execute(self, command: ProcessWebhookCommand):
        # 1. Ищем нашу транзакцию по ID от платежной системы
        transaction = await self.transaction_repo.find_by_external_id(command.external_payment_id)
        if not transaction:
            raise ValueError("Транзакция не найдена")

        if transaction.status != TransactionStatus.PENDING:
            return  # Уже обработано, игнорируем повторный вебхук

        # 2. Если оплата успешна
        if command.status == "succeeded":
            transaction.mark_success()
            await self.transaction_repo.save(transaction)

            # 3. Находим кошелек и пополняем его
            wallet = await self.wallet_repo.find_by_telegram_id(transaction.telegram_id)
            if not wallet:
                raise ValueError("Кошелек не найден")

            wallet.deposit(command.amount)
            await self.wallet_repo.save(wallet)