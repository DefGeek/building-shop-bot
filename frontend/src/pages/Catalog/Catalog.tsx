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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Загрузка товаров...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500 text-xl text-center px-6">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-md mx-auto">
        <div className="flex items-center justify-between mb-6">
          <Link to="/" className="text-blue-500 hover:text-blue-600 font-medium">
            ← На главную
          </Link>
          
          {totalItems > 0 && (
            <Link to="/cart" className="relative">
              <span className="text-2xl">🛍️</span>
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {totalItems}
              </span>
            </Link>
          )}
        </div>
        
        <h1 className="text-3xl font-bold text-gray-800 mb-6">🛒 Каталог</h1>
        
        <div className="space-y-4">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex gap-4 hover:shadow-md transition">
              <img 
                src={product.image_url || 'https://via.placeholder.com/100?text=No+Image'} 
                alt={product.name} 
                className="w-24 h-24 object-cover rounded-lg bg-gray-100 flex-shrink-0"
              />
              
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-lg text-gray-800 leading-tight">{product.name}</h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{product.description}</p>
                </div>
                
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xl font-bold text-blue-600">{product.price.toLocaleString('ru-RU')} ₽</span>
                  <button 
                    onClick={() => handleAddToCart(product)}
                    className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                      addedProductId === product.id
                        ? 'bg-green-500 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 active:scale-95 text-white'
                    }`}
                  >
                    {addedProductId === product.id ? '✓ Добавлено' : 'В корзину'}
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