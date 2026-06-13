import { Link } from 'react-router-dom';

export function Success() {
  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center justify-center text-center">
      <div className="text-6xl mb-4">🎉</div>
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Заказ успешно оформлен!</h1>
      <p className="text-gray-600 mb-8 max-w-sm">
        Спасибо за покупку. Мы уже получили уведомление и скоро свяжемся с вами для подтверждения.
      </p>
      <Link 
        to="/catalog" 
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg transition"
      >
        Вернуться в каталог
      </Link>
    </div>
  );
}
