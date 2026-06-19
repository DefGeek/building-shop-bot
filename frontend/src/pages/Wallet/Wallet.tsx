import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getWalletBalance, topUpWallet, mockPaymentSuccess } from '../../api/wallet';
import { useTelegram } from '../../hooks/useTelegram';

export function Wallet() {
  const { user } = useTelegram();
  const [balance, setBalance] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [topUpAmount, setTopUpAmount] = useState<string>('');
  const [isTopUping, setIsTopUping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    try {
      setLoading(true);
      const data = await getWalletBalance();
      setBalance(data.balance);
    } catch (err) {
      setError('Не удалось загрузить баланс');
    } finally {
      setLoading(false);
    }
  };

  const handleTopUp = async () => {
    const amount = parseFloat(topUpAmount);
    if (!amount || amount <= 0) {
      setError('Введите корректную сумму');
      return;
    }

    try {
      setIsTopUping(true);
      setError(null);

      const { payment_id } = await topUpWallet(amount);
      await mockPaymentSuccess(payment_id);

      await loadBalance();
      setSuccess(`Кошелек успешно пополнен на ${amount} ₽`);
      setTopUpAmount('');

      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка пополнения');
    } finally {
      setIsTopUping(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">💰</div>
          <div className="text-xl text-gray-700 font-semibold">Загрузка кошелька...</div>
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

        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent mb-6">
          💰 Кошелек
        </h1>

        {error && (
          <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-3 rounded-xl mb-4 font-semibold shadow-lg">
            ⚠️ {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border-2 border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4 font-semibold shadow-lg">
            ✅ {success}
          </div>
        )}

        <div className="bg-gradient-to-br from-white to-orange-50 rounded-2xl shadow-xl p-6 border border-orange-100 mb-6">
          <div className="text-center">
            <p className="text-gray-600 font-semibold mb-2">Ваш баланс</p>
            <p className="text-5xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
              {balance.toLocaleString('ru-RU')} ₽
            </p>
          </div>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-orange-100">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-2xl">💳</span> Пополнить кошелек
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Сумма (₽)</label>
              <input
                type="number"
                min="1"
                step="1"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                placeholder="Введите сумму"
                className="w-full border-2 border-orange-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition bg-white text-lg font-semibold"
              />
            </div>

            <div className="grid grid-cols-3 gap-2">
              {[100, 500, 1000].map((amount) => (
                <button
                  key={amount}
                  onClick={() => setTopUpAmount(amount.toString())}
                  className="bg-orange-50 hover:bg-orange-100 text-orange-700 font-semibold py-2 rounded-xl transition border border-orange-200"
                >
                  {amount} ₽
                </button>
              ))}
            </div>

            <button
              onClick={handleTopUp}
              disabled={isTopUping || !topUpAmount}
              className={`w-full py-4 rounded-xl font-bold text-lg text-white transition-all transform shadow-lg ${
                isTopUping || !topUpAmount
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 active:scale-95 hover:shadow-xl hover:scale-105'
              }`}
            >
              {isTopUping ? '💳 Обработка...' : '💰 Пополнить'}
            </button>
          </div>
        </div>

        <div className="mt-6 bg-yellow-50 border-2 border-yellow-300 rounded-2xl p-4 shadow-lg">
          <p className="text-yellow-800 text-sm font-semibold flex items-start gap-2">
            <span className="text-xl">ℹ️</span>
            <span>В тестовом режиме оплата имитируется. В реальной версии вы будете перенаправлены на страницу платежной системы.</span>
          </p>
        </div>
      </div>
    </div>
  );
}