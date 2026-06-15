import { Link } from 'react-router-dom';
import { useCartStore } from '../../store/cartStore';

export function Cart() {
  const items = useCartStore(state => state.items);
  const updateQuantity = useCartStore(state => state.updateQuantity);
  const removeFromCart = useCartStore(state => state.removeFromCart);
  const clearCart = useCartStore(state => state.clearCart);
  const getTotalPrice = useCartStore(state => state.getTotalPrice);

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
        <div className="max-w-md mx-auto text-center">
          <Link to="/" className="inline-block mb-6 text-orange-600 hover:text-orange-700 font-semibold transition">
            ← На главную
          </Link>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-6">
            🛍️ Корзина
          </h1>
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-12 border border-orange-100">
            <div className="text-7xl mb-4">🏗️</div>
            <p className="text-gray-700 text-xl font-semibold mb-2">Стройка не начата!</p>
            <p className="text-gray-500 mb-6">Добавьте материалы для вашего проекта</p>
            <Link
              to="/catalog"
              className="inline-block bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              🛒 Перейти в каталог
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
      <div className="max-w-md mx-auto">
        <Link to="/" className="inline-block mb-6 text-orange-600 hover:text-orange-700 font-semibold transition">
          ← На главную
        </Link>

        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            🛍️ Корзина
          </h1>
          <button
            onClick={clearCart}
            className="text-sm text-red-500 hover:text-red-600 font-semibold bg-red-50 hover:bg-red-100 px-3 py-1 rounded-lg transition"
          >
            🗑️ Очистить
          </button>
        </div>

        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.product.id} className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-orange-100 p-4 flex gap-4 hover:shadow-xl transition-all">
              <img
                src={item.product.image_url || 'https://via.placeholder.com/100?text=No+Image'}
                alt={item.product.name}
                className="w-24 h-24 object-cover rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex-shrink-0 shadow-md"
              />

              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-gray-800 text-lg">{item.product.name}</h3>
                  <p className="text-sm text-orange-600 font-semibold">{item.product.price.toLocaleString('ru-RU')} ₽</p>
                </div>

                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center gap-2 bg-orange-50 rounded-xl p-1">
                    <button
                      onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                      className="w-8 h-8 rounded-lg bg-white hover:bg-orange-100 flex items-center justify-center font-bold text-orange-600 shadow-sm transition"
                    >
                      −
                    </button>
                    <span className="font-bold w-8 text-center text-gray-800">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                      className="w-8 h-8 rounded-lg bg-white hover:bg-orange-100 flex items-center justify-center font-bold text-orange-600 shadow-sm transition"
                    >
                      +
                    </button>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="font-bold text-lg bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                      {(item.product.price * item.quantity).toLocaleString('ru-RU')} ₽
                    </span>
                    <button
                      onClick={() => removeFromCart(item.product.id)}
                      className="text-red-500 hover:text-red-600 hover:bg-red-50 p-2 rounded-lg transition"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 bg-gradient-to-br from-white to-orange-50 rounded-2xl shadow-xl p-6 border border-orange-100">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-semibold text-gray-700">Итого:</span>
            <span className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
              {getTotalPrice().toLocaleString('ru-RU')} ₽
            </span>
          </div>
          <Link to="/checkout" className="block w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-center text-lg">
            📦 Оформить заказ
          </Link>
        </div>
      </div>
    </div>
  );
}