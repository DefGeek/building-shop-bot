import { useTelegram } from '../../hooks/useTelegram';
import { useEffect, useState } from 'react';
import { authenticateWithTelegram, isAuthenticated } from '../../api/auth';
import { Link } from 'react-router-dom';

export function Home() {
  const { tg, user, isInTelegram } = useTelegram();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function authenticate() {
      console.log("🚀 [Home] Запуск авторизации...");
      
      const initData = tg?.initData || localStorage.getItem('tg_init_data');
      
      if (!initData) {
        console.warn("⚠️ [Home] Нет initData");
        setLoading(false);
        return;
      }

      try {
        if (!isAuthenticated()) {
          console.log("🔄 [Home] Запрашиваем токен...");
          await authenticateWithTelegram(initData);
          console.log("✅ [Home] Авторизация завершена!");
        } else {
          console.log("✅ [Home] Уже авторизован");
        }
        setLoading(false);
      } catch (err: any) {
        console.error("❌ [Home] Ошибка:", err);
        setError(err.response?.data?.detail || 'Ошибка авторизации');
        setLoading(false);
      }
    }

    authenticate();
  }, [tg]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Загрузка...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500 text-xl">❌ {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-md mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">🏗️ СтройМаркет AI</h1>
        
        {isInTelegram && user ? (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">✅ Добро пожаловать{user.first_name ? `, ${user.first_name}!` : '!'}</h2>
            <div className="space-y-2 text-gray-600">
              <p><strong>Telegram ID:</strong> {user.id}</p>
              {user.username && <p><strong>Username:</strong> @{user.username}</p>}
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
            <p className="text-yellow-800">⚠️ Приложение открыто вне Telegram.</p>
          </div>
        )}

        <div className="space-y-4">
          <Link to="/catalog" className="block w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition text-center">🛒 Каталог товаров</Link>
          <Link to="/cart" className="block w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition text-center">🛍️ Корзина</Link>
          <Link to="/profile" className="block w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition text-center">👤 Профиль</Link>
        </div>
      </div>
    </div>
  );
}