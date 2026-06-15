import { Link } from 'react-router-dom';
import { useTelegram } from '../../hooks/useTelegram';

export function Profile() {
  const { user } = useTelegram();

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 p-6">
      <div className="max-w-md mx-auto">
        <Link
          to="/"
          className="inline-block mb-6 text-orange-600 hover:text-orange-700 font-semibold transition"
        >
          ← Назад
        </Link>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-6">
          👤 Профиль
        </h1>

        <div className="bg-gradient-to-br from-white to-orange-50 rounded-2xl shadow-xl p-6 border border-orange-100">
          {user ? (
            <div className="space-y-4">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-amber-400 rounded-full flex items-center justify-center text-4xl shadow-lg">
                  👷
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    {user.first_name} {user.last_name || ''}
                  </h2>
                  {user.username && (
                    <p className="text-gray-600">@{user.username}</p>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <div className="bg-white rounded-xl p-4 shadow-sm border border-orange-100">
                  <p className="text-sm text-gray-500 font-semibold">Telegram ID</p>
                  <p className="text-lg font-bold text-gray-800">{user.id}</p>
                </div>

                {user.language_code && (
                  <div className="bg-white rounded-xl p-4 shadow-sm border border-orange-100">
                    <p className="text-sm text-gray-500 font-semibold">Язык</p>
                    <p className="text-lg font-bold text-gray-800 uppercase">{user.language_code}</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-5xl mb-4">👤</div>
              <p className="text-gray-600 font-semibold">Данные профиля недоступны</p>
            </div>
          )}
        </div>

        <div className="mt-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
          <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-2xl">📊</span> Статистика
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 text-center border border-orange-100">
              <div className="text-3xl font-bold text-orange-600">0</div>
              <div className="text-sm text-gray-600 font-semibold">Заказов</div>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl p-4 text-center border border-orange-100">
              <div className="text-3xl font-bold text-orange-600">0 ₽</div>
              <div className="text-sm text-gray-600 font-semibold">Потрачено</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}