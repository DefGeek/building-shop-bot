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

export async function authenticateWithTelegram(initData: string): Promise<AuthResponse> {
  console.log("🔐 [Auth] Начинаем запрос авторизации...");
  
  const response = await api.post<AuthResponse>('/auth/telegram', null, {
    headers: {
      'X-Telegram-Init-Data': initData,
    },
  });

  console.log("✅ [Auth] Ответ от сервера получен");

  if (response.data.access_token) {
    // ⚠️ ВАЖНО: Сохраняем в cookie вместо localStorage
    setCookie('access_token', response.data.access_token, 7);
    console.log("💾 [Auth] Токен сохранен в cookie!");
  } else {
    console.error("❌ [Auth] Токен не найден в ответе!");
  }

  return response.data;
}

export function logout() {
  deleteCookie('access_token');
  window.location.reload();
}

export function isAuthenticated(): boolean {
  const token = getCookie('access_token');
  console.log("🔍 [Auth] Проверка токена в cookie:", token ? "ЕСТЬ" : "НЕТ");
  return !!token;
}