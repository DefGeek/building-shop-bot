import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartStore } from '../../store/cartStore';
import { createOrder } from '../../api/orders';
import { useTelegram } from '../../hooks/useTelegram';

export function Checkout() {
  const navigate = useNavigate();
  const { user } = useTelegram();
  const items = useCartStore(state => state.items);
  const getTotalPrice = useCartStore(state => state.getTotalPrice);
  const clearCart = useCartStore(state => state.clearCart);

  const [formData, setFormData] = useState({
    customer_name: user?.first_name || '',
    phone: '',
    address: '',
    comment: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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

      await createOrder(orderPayload);
      clearCart();
      navigate('/success');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при оформлении заказа. Попробуйте позже.');
    } finally {
      setIsSubmitting(false);
    }
  };

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

          <div className="bg-gradient-to-br from-white to-orange-50 p-6 rounded-2xl shadow-xl border border-orange-100">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-700 font-semibold">Товаров в заказе:</span>
              <span className="text-xl font-bold text-orange-600">{items.reduce((acc, item) => acc + item.quantity, 0)} шт.</span>
            </div>
            <div className="flex justify-between items-center text-xl font-bold border-t-2 border-orange-200 pt-4">
              <span className="text-gray-800">Итого к оплате:</span>
              <span className="text-2xl bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                {getTotalPrice().toLocaleString('ru-RU')} ₽
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-4 rounded-xl font-bold text-lg text-white transition-all transform shadow-lg ${
              isSubmitting
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