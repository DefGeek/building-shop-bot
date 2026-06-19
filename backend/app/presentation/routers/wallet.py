from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_telegram_id
from app.infrastructure.repositories.wallet_repository_impl import WalletRepositoryImpl
from app.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
from app.infrastructure.payment.mock_payment_gateway import MockPaymentGateway

from app.application.wallet.queries.get_wallet_balance import GetWalletBalanceHandler, GetWalletBalanceQuery
from app.application.wallet.commands.top_up_wallet import TopUpWalletHandler, TopUpWalletCommand
from app.application.wallet.commands.process_payment_webhook import ProcessPaymentWebhookHandler, ProcessWebhookCommand

router = APIRouter(prefix="/wallet", tags=["wallet"])

# Инициализируем мок-шлюз (в реальности он был бы один на все приложение)
mock_gateway = MockPaymentGateway()


@router.get("/balance")
async def get_balance(
        telegram_id: int = Depends(get_current_telegram_id),
        db: AsyncSession = Depends(get_db),
):
    wallet_repo = WalletRepositoryImpl(db)
    handler = GetWalletBalanceHandler(wallet_repo)
    result = await handler.execute(GetWalletBalanceQuery(telegram_id=telegram_id))
    return {"telegram_id": result.telegram_id, "balance": result.balance}


@router.post("/top-up")
async def top_up(
        amount: float,
        telegram_id: int = Depends(get_current_telegram_id),
        db: AsyncSession = Depends(get_db),
):
    """Создает платеж и возвращает ссылку на оплату"""
    wallet_repo = WalletRepositoryImpl(db)
    transaction_repo = TransactionRepositoryImpl(db)

    handler = TopUpWalletHandler(wallet_repo, transaction_repo, mock_gateway)
    result = await handler.execute(TopUpWalletCommand(telegram_id=telegram_id, amount=amount))

    return {"payment_id": result.payment_id, "confirmation_url": result.confirmation_url}


@router.post("/webhooks/payment")
async def payment_webhook(
        payload: dict,
        db: AsyncSession = Depends(get_db)
):
    """Эмуляция вебхука от ЮKassa"""
    # В реальной ЮKassa тут была бы проверка подписи (signature)

    # Ожидаем формат: {"event": "payment.succeeded", "object": {"id": "mock_pay_...", "amount": {"value": "100.00"}}}
    event = payload.get("event")
    obj = payload.get("object", {})

    if event == "payment.succeeded":
        handler = ProcessPaymentWebhookHandler(
            WalletRepositoryImpl(db),
            TransactionRepositoryImpl(db)
        )
        await handler.execute(ProcessWebhookCommand(
            external_payment_id=obj.get("id"),
            status="succeeded",
            amount=float(obj.get("amount", {}).get("value", 0))
        ))
        return {"status": "ok"}

    raise HTTPException(status_code=400, detail="Unsupported event")


# 🔥 УТИЛИТА ДЛЯ ТЕСТА: Имитирует успешную оплату одним кликом
@router.post("/mock-success/{payment_id}")
async def mock_success(payment_id: str, db: AsyncSession = Depends(get_db)):
    """Этот эндпоинт только для тестов: имитирует приход вебхука об успехе"""
    handler = ProcessPaymentWebhookHandler(
        WalletRepositoryImpl(db),
        TransactionRepositoryImpl(db)
    )
    # Для теста берем сумму 100, в реальности она пришла бы в вебхуке
    await handler.execute(ProcessWebhookCommand(
        external_payment_id=payment_id,
        status="succeeded",
        amount=100.0
    ))
    return {"status": "simulated_success"}