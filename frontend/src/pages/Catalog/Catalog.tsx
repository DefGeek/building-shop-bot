import { Link } from 'react-router-dom';

export function Catalog() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-md mx-auto">
        <Link
          to="/"
          className="inline-block mb-6 text-blue-500 hover:text-blue-600"
        >
          ← Назад
        </Link>
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          🛒 Каталог товаров
        </h1>
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-600">Список товаров будет здесь</p>
        </div>
      </div>
    </div>
  );
}