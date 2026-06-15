import { Link } from 'react-router-dom';

export function Success() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 p-6 flex flex-col items-center justify-center text-center">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-10 border border-green-200 max-w-md">
        <div className="text-8xl mb-6 animate-bounce">🎉</div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
          Заказ оформлен!
        </h1>
        <p className="text-gray-700 text-lg mb-2 font-semibold">
          Спасибо за покупку!
        </p>
        <p className="text-gray-600 mb-8">
          Мы уже получили ваш заказ и скоро свяжемся с вами для подтверждения доставки.
        </p>

        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 mb-6 border border-green-200">
          <div className="text-4xl mb-2">🚚</div>
          <p className="text-gray-700 font-semibold">Ожидайте звонка</p>
          <p className="text-sm text-gray-600">в течение 30 минут</p>
        </div>

        <Link
          to="/catalog"
          className="inline-block bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-bold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 text-lg"
        >
          🛒 Вернуться в каталог
        </Link>
      </div>
    </div>
  );
}