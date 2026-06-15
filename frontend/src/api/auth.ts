import api, { setCookie, getCookie, deleteCookie } from './client';

export interface AuthResponse {
  user_id: string;
  telegram_id: number;
  first_name: string;
  full_name: string;
  role: string;
  is_new_user: boolean;
  access_token: string;
}

// в данных юзера+HASH к ним тг добавляет заголовок
// X-Telegram-Init-Data его шлём на бэкенд в /auth/telegram
// когда получаем успешный ответ то сохраняем его в cookie access_token
export async function authenticateWithTelegram(initData: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/telegram', null, {
    headers: {
      'X-Telegram-Init-Data': initData,
    },
  });

  if (response.data.access_token) {
    setCookie('access_token', response.data.access_token, 7);
  }

  return response.data;
}

export function logout() {
  deleteCookie('access_token');
  window.location.reload();
}

export function isAuthenticated(): boolean {
  const token = getCookie('access_token');
  return !!token;
}