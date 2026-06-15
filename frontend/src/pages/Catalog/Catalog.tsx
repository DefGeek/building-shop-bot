import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getProducts, type Product } from '../../api/products-api';
import { useCartStore } from '../../store/cartStore';

export function Catalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addedProductId, setAddedProductId] = useState<number | null>(null);
  
  const addToCart = useCartStore(state => state.addToCart);
  const totalItems = useCartStore(state => state.getTotalItems());

  useEffect(() => {
    async function fetchProducts() {
      try {
        setLoading(true);
        const data = await getProducts();
        setProducts(data);
      } catch (err) {
        setError('Не удалось загрузить товары. Проверьте соединение.');
      } finally {
        setLoading(false);
      }
    }
    fetchProducts();
  }, []);

  const handleAddToCart = (product: Product) => {
    addToCart(product);
    setAddedProductId(product.id);
    setTimeout(() => setAddedProductId(null), 1500);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">🏗️</div>
          <div className="text-xl text-gray-700 font-semibold">Загружаем материалы...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-red-200 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <div className="text-red-600 text-xl font-semibold">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Link to="/" className="text-orange-600 hover:text-orange-700 font-semibold transition">
            ← На главную
          </Link>

          {totalItems > 0 && (
            <Link to="/cart" className="relative group">
              <div className="bg-gradient-to-br from-orange-500 to-amber-500 p-3 rounded-xl shadow-lg group-hover:shadow-xl transition-all transform group-hover:scale-110">
                <span className="text-2xl">🛍️</span>
              </div>
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg animate-pulse">
                {totalItems}
              </span>
            </Link>
          )}
        </div>

        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-6">
          🛒 Каталог материалов
        </h1>

        <div className="space-y-4">
          {products.map((product) => (
            <div key={product.id} className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-orange-100 p-4 flex gap-4 hover:shadow-xl transition-all transform hover:scale-[1.02]">
              <img
                src={product.image_url || 'https://via.placeholder.com/100?text=No+Image'}
                alt={product.name}
                className="w-28 h-28 object-cover rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex-shrink-0 shadow-md"
              />

              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-lg text-gray-800 leading-tight">{product.name}</h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{product.description}</p>
                </div>

                <div className="flex items-center justify-between mt-3">
                  <span className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                    {product.price.toLocaleString('ru-RU')} ₽
                  </span>
                  <button
                    onClick={() => handleAddToCart(product)}
                    className={`px-5 py-2 rounded-xl text-sm font-bold transition-all transform active:scale-95 shadow-lg ${
                      addedProductId === product.id
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                        : 'bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white hover:shadow-xl hover:scale-105'
                    }`}
                  >
                    {addedProductId === product.id ? '✓ Добавлено' : '🛒 В корзину'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}