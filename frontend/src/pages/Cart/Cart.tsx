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
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-md mx-auto text-center">
          <Link to="/" className="inline-block mb-6 text-blue-500 hover:text-blue-600 font-medium">
            ← На главную
          </Link>
          <h1 className="text-3xl font-bold text-gray-800 mb-6">🛍️ Корзина</h1>
          <div className="bg-white rounded-xl shadow-sm p-12">
            <p className="text-6xl mb-4">🛒</p>
            <p className="text-gray-600 text-lg">Ваша корзина пуста</p>
            <Link 
              to="/catalog" 
              className="inline-block mt-6 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              Перейти в каталог
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-md mx-auto">
        <Link to="/" className="inline-block mb-6 text-blue-500 hover:text-blue-600 font-medium">
          ← На главную
        </Link>
        
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-800">🛍️ Корзина</h1>
          <button 
            onClick={clearCart}
            className="text-sm text-red-500 hover:text-red-600 font-medium"
          >
            Очистить
          </button>
        </div>
        
        <div className="space-y-4">
          {items.map((item) => (
            <div key={item.product.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex gap-4">
              <img 
                src={item.product.image_url || 'https://via.placeholder.com/100?text=No+Image'} 
                alt={item.product.name} 
                className="w-20 h-20 object-cover rounded-lg bg-gray-100 flex-shrink-0"
              />
              
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-gray-800">{item.product.name}</h3>
                  <p className="text-sm text-gray-500">{item.product.price.toLocaleString('ru-RU')} ₽</p>
                </div>
                
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                      className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center font-bold"
                    >
                      -
                    </button>
                    <span className="font-semibold w-8 text-center">{item.quantity}</span>
                    <button 
                      onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                      className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center font-bold"
                    >
                      +
                    </button>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-blue-600">
                      {(item.product.price * item.quantity).toLocaleString('ru-RU')} ₽
                    </span>
                    <button 
                      onClick={() => removeFromCart(item.product.id)}
                      className="text-red-500 hover:text-red-600 text-xl"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-6 bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-lg font-semibold text-gray-700">Итого:</span>
            <span className="text-2xl font-bold text-blue-600">
              {getTotalPrice().toLocaleString('ru-RU')} ₽
            </span>
          </div>
          <Link to="/checkout" className="block w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 rounded-lg transition text-center text-lg">
                Оформить заказ
          </Link>
        </div>
      </div>
    </div>
  );
}