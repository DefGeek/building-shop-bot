# СтройМаркет

Telegram Mini App для продажи строительных материалов с внутренним кошельком и системой заказов.

## Запуск

```bash
docker-compose up --build
npm run dev
ngrok http 3000
```

После запуска:
- Backend API: `http://localhost:8000` (документация: `http://localhost:8000/docs`)
- Frontend: `http://localhost:5173`
- База данных: `localhost:5432`

Не забудь создать `.env` файл:
```env
TELEGRAM_BOT_TOKEN=ваш_токен
SECRET_KEY=ваш_ключ
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/stroymarket_db
```

## Что делает бот

Бот решает задачу продаж строительных материалов через Telegram. Пользователь открывает Mini App, просматривает каталог товаров, добавляет их в корзину и оформляет заказ.

Основные возможности:
- Каталог товаров с ценами и описаниями
- Корзина с сохранением между сессиями
- Внутренний кошелек пользователя (пополнение и списание)
- Оплата заказа с кошелька или картой (в тестовом режиме)
- Уведомления админу в Telegram о новых заказах

Сейчас реализована базовая функциональность: авторизация через Telegram, каталог, корзина, заказы и кошелёк. Платежная система работает в мок-режиме для тестирования.

## Технические детали

### Архитектура DDD

Проект построен по принципам Domain-Driven Design с разделением на 4 слоя:

**Domain** — ядро системы. Здесь живут бизнес-сущности (`Order`, `Wallet`, `Transaction`), value objects (`TelegramID`) и интерфейсы (порты) репозиториев. Domain не знает ни о базе данных, ни о HTTP, ни о Telegram. Он описывает бизнес-правила: как создать заказ, как списать деньги с кошелька, какие проверки нужно пройти.

**Application** — сценарии использования. Здесь реализуются use cases через команды (Commands) и запросы (Queries). Например, `PayOrderFromWalletHandler` получает на вход порты репозиториев и выполняет бизнес-операцию: находит заказ, проверяет владельца, списывает деньги, обновляет статус. Application layer оркестрирует процесс, но не содержит бизнес-логики — она вся в Domain.

**Infrastructure** — реализация портов. Здесь лежат SQLAlchemy модели, конкретные репозитории (`OrderRepositoryImpl`, `WalletRepositoryImpl`), JWT-генераторы, Telegram-клиенты. Infrastructure знает всё о внешних зависимостях и реализует интерфейсы из Domain. Когда Application вызывает `wallet_repo.save(wallet)`, он не знает, что это SQLAlchemy — он просто использует порт.

**Presentation** — точки входа. FastAPI роутеры принимают HTTP-запросы, извлекают данные (JWT из cookie, telegram_id из токена), создают экземпляры Application handlers, передают им зависимости из Infrastructure и возвращают ответ. Presentation layer тонкий — он только адаптирует HTTP к внутренним сценариям.

Пример потока данных:
```
HTTP Request → Presentation (роутер) → Application (handler) → Domain (сущности) → Infrastructure (репозиторий) → PostgreSQL
```

### Авторизация и JWT

Пользователь открывает Mini App в Telegram. Telegram передает `initData` (подписанные данные о пользователе) через JavaScript SDK. Frontend отправляет `initData` на backend через `POST /api/v1/auth/telegram`.

Backend проверяет подпись `initData` через `TelegramAuthVerifier` (использует токен бота для HMAC-SHA256). Если подпись валидна, извлекает `telegram_id` и создает пользователя в БД (если его нет).

Затем генерируется JWT токен с `telegram_id` в payload. Токен подписывается секретным ключом (`SECRET_KEY`) алгоритмом HS256. Токен устанавливается в cookie `access_token` с флагами:
- `httponly=True` — недоступна из JavaScript (защита от XSS)
- `secure=True` — передается только по HTTPS
- `samesite="none"` — работает в iframe Telegram (cross-site)
- `max_age=7 дней`

При каждом запросе frontend автоматически отправляет cookie. Backend извлекает токен через зависимость `get_current_telegram_id`, проверяет подпись JWT и возвращает `telegram_id`. Этот ID используется во всех операциях (создание заказа, пополнение кошелька и т.д.).

### Система оплаты

Оплата реализована через внутренний кошелек. У каждого пользователя есть `Wallet` с балансом. При создании заказа (`POST /api/v1/orders/`) заказ сохраняется со статусом `new`.

Если пользователь выбирает оплату с кошелька, frontend вызывает `POST /api/v1/orders/{id}/pay`. Backend:
1. Находит заказ по ID
2. Проверяет, что `order.telegram_id == current_user.telegram_id` (защита от чужих заказов)
3. Проверяет, что статус заказа `new` (нельзя оплатить дважды)
4. Находит кошелек пользователя
5. Проверяет, что `wallet.balance >= order.total_price`
6. Вызывает `wallet.withdraw(amount)` — бизнес-метод из Domain, который проверяет баланс и уменьшает его
7. Сохраняет кошелек через репозиторий
8. Создает транзакцию со статусом `SUCCESS`
9. Обновляет статус заказа на `paid`

Всё это происходит в одной транзакции БД. Если что-то падает (недостаточно средств, заказ уже оплачен), выбрасывается исключение, и ничего не сохраняется.

Для тестирования используется `MockPaymentGateway`, который имитирует создание платежа и возвращает фейковую ссылку. В реальности здесь будет интеграция с ЮKassa или другим провайдером.

### Структура проекта

```
backend/app/
├── domain/
│   ├── order/
│   │   ├── entities/          # Order, OrderItem
│   │   └── ports/             # OrderRepository (интерфейс)
│   ├── wallet/
│   │   ├── entities/          # Wallet, Transaction
│   │   └── ports/             # WalletRepository, PaymentGateway
│   └── user/
│       ├── entities/          # User
│       └── value_objects/     # TelegramID
├── application/
│   ├── orders/commands/       # CreateOrderHandler, PayOrderFromWalletHandler
│   └── wallet/
│       ├── commands/          # TopUpWalletHandler, ProcessPaymentWebhookHandler
│       └── queries/           # GetWalletBalanceHandler
├── infrastructure/
│   ├── database/models/       # SQLAlchemy модели (OrderModel, WalletModel)
│   ├── repositories/          # OrderRepositoryImpl, WalletRepositoryImpl
│   ├── security/              # JWT генератор и верификатор
│   └── payment/               # MockPaymentGateway
└── presentation/
    ├── routers/               # FastAPI эндпоинты (orders.py, wallet.py, auth.py)
    ├── dependencies.py        # get_current_telegram_id
    └── schemas/               # Pydantic модели для валидации
```

### Асинхронность

Весь backend асинхронный (FastAPI + SQLAlchemy 2.0 async). Бот и API работают в одном event loop через `asyncio.gather`. Это позволяет обрабатывать много запросов одновременно без блокировок.

### База данных

PostgreSQL с таблицами:
- `users` — telegram_id, username, created_at
- `products` — name, description, price, image_url, is_available
- `orders` — telegram_id, total_price, status, payment_method, customer_name, phone, address
- `order_items` — order_id, product_id, quantity, price
- `wallets` — telegram_id, balance
- `transactions` — telegram_id, amount, status, external_payment_id

Все связи через foreign keys. Для заказов используется one-to-many (один заказ — много позиций). Для кошелька one-to-one (один пользователь — один кошелек).