import { useTelegram } from '../../hooks/useTelegram';
import { useEffect, useState } from 'react';
import { authenticateWithTelegram, isAuthenticated } from '../../api/auth';
import { Link } from 'react-router-dom';

export function Home() {
  const { tg, user, isInTelegram } = useTelegram();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // useEffect - хук который нужен для взаимодействия с внешним
  // миром, а не просто для возвращения разметки
  useEffect(() => {
    async function authenticate() {
      const initData = tg?.initData;

      if (!initData) {
        setLoading(false);
        return;
      }

      try {
        if (!isAuthenticated()) {
          // отправляем initData для проверки на бэкенд
          await authenticateWithTelegram(initData);
        }
        setLoading(false);
      } catch (err: any) {
        console.error("Ошибка:", err);
        setError(err.response?.data?.detail || 'Ошибка авторизации');
        setLoading(false);
      }
    }

    authenticate();
  }, [tg]); // [tg] говорит выполняй этот эффект при первом рендере и при каждом изменении tg

  if (!isInTelegram) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center p-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-orange-100 text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Откройте через Telegram</h2>
          <p className="text-gray-600">Это приложение работает только внутри Telegram Mini App</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">🏗️</div>
          <div className="text-xl text-gray-700 font-semibold">Подготовка стройки...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-red-200 text-center">
          <div className="text-5xl mb-4">❌</div>
          <div className="text-red-600 text-xl font-semibold">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">🏗️</div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-2">
            СтройМаркет
          </h1>
          <p className="text-gray-600 font-semibold">Ваш надежный поставщик материалов</p>
        </div>

        {isInTelegram && user ? (
          <div className="bg-gradient-to-br from-white to-orange-50 rounded-2xl shadow-xl p-6 mb-6 border border-orange-100">
            <div className="flex items-center gap-3">
              <div className="text-4xl">👷</div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Добро пожаловать!</h2>
                <p className="text-sm text-gray-600">Готовы начать строительство?</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-2xl p-6 mb-6 shadow-lg">
            <p className="text-yellow-800 font-semibold flex items-center gap-2">
              <span className="text-2xl">⚠️</span> Приложение открыто вне Telegram.
            </p>
          </div>
        )}

        <div className="space-y-4">
          <Link to="/catalog" className="block w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-center text-lg">
            🛒 Каталог материалов
          </Link>
          <Link to="/wallet" className="block w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-center text-lg">
            💰 Кошелек
          </Link>
          <Link to="/cart" className="block w-full bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-800 font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-center text-lg border border-gray-300">
            🛍️ Корзина
          </Link>
          <Link to="/profile" className="block w-full bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-800 font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-center text-lg border border-gray-300">
            👤 Профиль
          </Link>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>🔒 Безопасные платежи</p>
          <p>🚚 Быстрая доставка</p>
          <p>⭐ Гарантия качества</p>
        </div>
      </div>
    </div>
  );
}