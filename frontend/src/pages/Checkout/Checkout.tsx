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
      <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center justify-center">
        <h2 className="text-2xl font-bold mb-4">Корзина пуста</h2>
        <Link to="/catalog" className="text-blue-500 hover:underline">Вернуться в каталог</Link>
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
      clearCart(); // Очищаем корзину после успешного заказа
      navigate('/success'); // Перенаправляем на страницу успеха
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при оформлении заказа. Попробуйте позже.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-md mx-auto">
        <Link to="/cart" className="inline-block mb-6 text-blue-500 hover:text-blue-600 font-medium">
          ← Вернуться в корзину
        </Link>
        
        <h1 className="text-3xl font-bold text-gray-800 mb-6">📦 Оформление заказа</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Данные клиента */}
          <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
            <h2 className="font-semibold text-lg">Контактные данные</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
              <input
                type="text"
                required
                value={formData.customer_name}
                onChange={e => setFormData({...formData, customer_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input
                type="tel"
                required
                placeholder="+7 (999) 000-00-00"
                value={formData.phone}
                onChange={e => setFormData({...formData, phone: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Адрес доставки</label>
              <textarea
                required
                rows={2}
                value={formData.address}
                onChange={e => setFormData({...formData, address: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Комментарий (необязательно)</label>
              <textarea
                rows={2}
                value={formData.comment}
                onChange={e => setFormData({...formData, comment: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Итого */}
          <div className="bg-white p-4 rounded-xl shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <span className="text-gray-600">Товаров в заказе: {items.reduce((acc, item) => acc + item.quantity, 0)} шт.</span>
            </div>
            <div className="flex justify-between items-center text-xl font-bold border-t pt-4">
              <span>Итого к оплате:</span>
              <span className="text-blue-600">{getTotalPrice().toLocaleString('ru-RU')} ₽</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-4 rounded-xl font-bold text-lg text-white transition ${
              isSubmitting ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600 active:scale-95'
            }`}
          >
            {isSubmitting ? 'Оформляем...' : 'Подтвердить заказ'}
          </button>
        </form>
      </div>
    </div>
  );
}
