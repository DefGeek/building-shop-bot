import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartStore } from '../../store/cartStore';
import { createOrder } from '../../api/orders';
import { useTelegram } from '../../hooks/useTelegram';
import { getWalletBalance, payOrderFromWallet } from '../../api/wallet';

export function Checkout() {
  const navigate = useNavigate();
  const { user } = useTelegram();
  const items = useCartStore(state => state.items);
  const getTotalPrice = useCartStore(state => state.getTotalPrice);
  const clearCart = useCartStore(state => state.clearCart);

  const [walletBalance, setWalletBalance] = useState<number>(0);
  const [paymentMethod, setPaymentMethod] = useState<'wallet' | 'card'>('wallet');
  const [formData, setFormData] = useState({
    customer_name: user?.first_name || '',
    phone: '',
    address: '',
    comment: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWalletBalance();
  }, []);

  const loadWalletBalance = async () => {
    try {
      const data = await getWalletBalance();
      setWalletBalance(data.balance);
    } catch (err) {
      console.error('Не удалось загрузить баланс кошелька');
    }
  };

  // ✅ handleSubmit ОПРЕДЕЛЕН ДО условного return
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isSubmitting) {
      console.log("⚠️ SUBMIT - already submitting, ignoring");
      return;
    }

    console.log("🔍 SUBMIT - start");
    setIsSubmitting(true);
    setError(null);

    try {
      const orderPayload = {
        ...formData,
        items: items.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity
        }))
      };

      console.log("🔍 SUBMIT - payload:", orderPayload);
      console.log("🔍 SUBMIT - paymentMethod:", paymentMethod);
      console.log("🔍 SUBMIT - walletBalance BEFORE:", walletBalance);
      console.log("🔍 SUBMIT - total:", getTotalPrice());

      const orderResponse = await createOrder(orderPayload);
      console.log("✅ SUBMIT - orderResponse:", orderResponse);

      const orderId = orderResponse.order_id;
      console.log("🔍 SUBMIT - orderId:", orderId);

      if (!orderId) {
        setError('Не удалось получить ID заказа');
        setIsSubmitting(false);
        return;
      }

      if (paymentMethod === 'wallet') {
        if (walletBalance < getTotalPrice()) {
          setError('Недостаточно средств на кошельке');
          setIsSubmitting(false);
          return;
        }

        console.log("🔍 SUBMIT - paying from wallet...");
        const payResponse = await payOrderFromWallet(orderId);
        console.log("✅ SUBMIT - payResponse:", payResponse);

        if (!payResponse.success) {
          setError(payResponse.message || 'Ошибка оплаты');
          setIsSubmitting(false);
          return;
        }

        console.log("✅ SUBMIT - new_balance from server:", payResponse.new_balance);
      }

      clearCart();
      navigate('/success');
    } catch (err: any) {
      console.error("❌ SUBMIT ERROR:", err);
      console.error("❌ SUBMIT ERROR response:", err.response);
      console.error("❌ SUBMIT ERROR data:", err.response?.data);

      let errorMessage = 'Ошибка при оформлении заказа. Попробуйте позже.';

      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((e: any) => e.msg).join(', ');
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (typeof err.response.data.detail === 'object') {
          errorMessage = JSON.stringify(err.response.data.detail);
        }
      }

      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // ✅ Теперь условный return ПОСЛЕ всех определений
  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6 flex flex-col items-center justify-center">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-orange-100 text-center">
          <div className="text-6xl mb-4">🏗️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Корзина пуста</h2>
          <p className="text-gray-600 mb-6">Добавьте материалы для оформления заказа</p>
          <Link to="/catalog" className="inline-block bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
            🛒 Вернуться в каталог
          </Link>
        </div>
      </div>
    );
  }

  const total = getTotalPrice();
  const canPayWithWallet = walletBalance >= total;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
      <div className="max-w-md mx-auto">
        <Link to="/cart" className="inline-block mb-6 text-orange-600 hover:text-orange-700 font-semibold transition">
          ← Вернуться в корзину
        </Link>

        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-6">
          📦 Оформление заказа
        </h1>

        {error && (
          <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-3 rounded-xl mb-4 font-semibold shadow-lg">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Контактные данные */}
          <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-xl border border-orange-100 space-y-4">
            <h2 className="font-bold text-xl text-gray-800 flex items-center gap-2">
              <span className="text-2xl">👷</span> Контактные данные
            </h2>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Имя</label>
              <input
                type="text"
                required
                value={formData.customer_name}
                onChange={e => setFormData({...formData, customer_name: e.target.value})}
                className="w-full border-2 border-orange-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Телефон</label>
              <input
                type="tel"
                required
                placeholder="+7 (999) 000-00-00"
                value={formData.phone}
                onChange={e => setFormData({...formData, phone: e.target.value})}
                className="w-full border-2 border-orange-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition bg-white"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Адрес доставки</label>
              <textarea
                required
                rows={2}
                value={formData.address}
                onChange={e => setFormData({...formData, address: e.target.value})}
                className="w-full border-2 border-orange-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition bg-white resize-none"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Комментарий (необязательно)</label>
              <textarea
                rows={2}
                value={formData.comment}
                onChange={e => setFormData({...formData, comment: e.target.value})}
                className="w-full border-2 border-orange-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition bg-white resize-none"
              />
            </div>
          </div>

          {/* Способ оплаты */}
          <div className="bg-white/90 backdrop-blur-sm p-6 rounded-2xl shadow-xl border border-orange-100">
            <h2 className="font-bold text-xl text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">💳</span> Способ оплаты
            </h2>

            <div className="space-y-3">
              <label className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition ${
                paymentMethod === 'wallet'
                  ? 'border-orange-500 bg-orange-50'
                  : 'border-gray-200 hover:border-orange-300'
              }`}>
                <input
                  type="radio"
                  name="payment"
                  value="wallet"
                  checked={paymentMethod === 'wallet'}
                  onChange={() => setPaymentMethod('wallet')}
                  className="w-5 h-5 text-orange-600"
                />
                <div className="flex-1">
                  <div className="font-bold text-gray-800">💰 С кошелька</div>
                  <div className="text-sm text-gray-600">
                    Баланс: <span className="font-semibold text-orange-600">{walletBalance.toLocaleString('ru-RU')} ₽</span>
                  </div>
                  {!canPayWithWallet && (
                    <div className="text-xs text-red-600 mt-1">Недостаточно средств</div>
                  )}
                </div>
              </label>

              <label className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition ${
                paymentMethod === 'card'
                  ? 'border-orange-500 bg-orange-50'
                  : 'border-gray-200 hover:border-orange-300'
              }`}>
                <input
                  type="radio"
                  name="payment"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={() => setPaymentMethod('card')}
                  className="w-5 h-5 text-orange-600"
                />
                <div className="flex-1">
                  <div className="font-bold text-gray-800">💳 Банковская карта</div>
                  <div className="text-sm text-gray-600">Оплата через платежную систему</div>
                </div>
              </label>
            </div>
          </div>

          {/* Итого */}
          <div className="bg-gradient-to-br from-white to-orange-50 p-6 rounded-2xl shadow-xl border border-orange-100">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-semibold">Товаров в заказе:</span>
              <span className="text-xl font-bold text-orange-600">{items.reduce((acc, item) => acc + item.quantity, 0)} шт.</span>
            </div>
            <div className="flex justify-between items-center text-xl font-bold border-t-2 border-orange-200 pt-4">
              <span className="text-gray-800">Итого к оплате:</span>
              <span className="text-2xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                {total.toLocaleString('ru-RU')} ₽
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || (paymentMethod === 'wallet' && !canPayWithWallet)}
            className={`w-full py-4 rounded-xl font-bold text-lg text-white transition-all transform shadow-lg ${
              isSubmitting || (paymentMethod === 'wallet' && !canPayWithWallet)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 active:scale-95 hover:shadow-xl hover:scale-105'
            }`}
          >
            {isSubmitting ? '🏗️ Оформляем...' : '✓ Подтвердить заказ'}
          </button>
        </form>
      </div>
    </div>
  );
}