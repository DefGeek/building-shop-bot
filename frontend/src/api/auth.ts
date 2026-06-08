//менеджер авторизации
import api from './client';

//создаём inerface для получения данных в таком формате
// от бэкенда. Это нужно,чтоб TypeScript проверял,что
// мы правильно работаем с ответом
export interface AuthResponse {
  user_id: string;
  telegram_id: number;
  first_name: string;
  full_name: string;
  role: string;
  is_new_user: boolean;
  access_token: string;
}


//функция входа через Telegram
//export — функция доступна для импорта в других файлах
//async — функция асинхронная (делает HTTP-запрос, который занимает время)
//initData: string — принимает строку initData от Telegram
//: Promise<AuthResponse> — возвращает Promise, который в итоге станет объектом AuthResponse
export async function authenticateWithTelegram(initData: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/telegram', null, {
    headers: {
      'X-Telegram-Init-Data': initData,
    },
  });

  // Сохраняем токен
  localStorage.setItem('access_token', response.data.access_token);

  return response.data;
}

//Функция выхода из аккаунта
export function logout() {
  localStorage.removeItem('access_token');
  window.location.reload();
}

//проверка пользователя на авторизацию
export function isAuthenticated(): boolean {
  // !! превращает любое значение в boolean
  return !!localStorage.getItem('access_token');
}