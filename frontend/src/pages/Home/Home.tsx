import { useTelegram } from '../../hooks/useTelegram';
import { useEffect, useState } from 'react';
import { authenticateWithTelegram, isAuthenticated } from '../../api/auth';

export function Home() {
  const { tg, user, isInTelegram } = useTelegram(); // Получаем данные от Telegram
  const [loading, setLoading] = useState(true); // когда компоненты загрузились, мы не знаем - авторизован ли юзер, и ставим загрузку - true
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function authenticate() {
      if (!tg?.initData) {
        setLoading(false);
        return;
      }

      try {
        if (!isAuthenticated()) { // Если нет токена в localStorage
          await authenticateWithTelegram(tg.initData); // Отправляем initData на backend
        }
        setLoading(false);
      } catch (err: any) {
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
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          🏗️ СтройМаркет AI
        </h1>

        {isInTelegram && user ? (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              ✅ Добро пожаловать, {user.first_name}!
            </h2>
            <div className="space-y-2 text-gray-600">
              <p><strong>Telegram ID:</strong> {user.id}</p>
              {user.username && <p><strong>Username:</strong> @{user.username}</p>}
              <p><strong>Язык:</strong> {user.language_code || 'не определен'}</p>
            </div>
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <p className="text-green-700 text-sm">
                ✓ Авторизация успешна<br />
                ✓ JWT токен получен и сохранен
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-yellow-800">
              ⚠️ Приложение открыто вне Telegram.<br />
              Для полной функциональности откройте через бота.
            </p>
          </div>
        )}

        <div className="mt-8 space-y-4">
          <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition">
            🛒 Каталог товаров
          </button>
          <button className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition">
            🛍️ Корзина
          </button>
          <button className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition">
            👤 Профиль
          </button>
        </div>
      </div>
    </div>
  );
}