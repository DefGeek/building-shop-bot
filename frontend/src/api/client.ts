import axios from 'axios';

const baseURL = '/api/v1';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = getCookie('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('🔑 [API] Токен добавлен к запросу');
  } else {
    console.warn('⚠️ [API] Токен НЕ найден в cookie!');
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ [API] 401 Unauthorized - удаляем cookie и перезагружаем');
      // ⚠️ ВАЖНО: Удаляем cookie и перезагружаем страницу
      deleteCookie('access_token');
      console.log('🗑️ [API] Cookie access_token удалена');
      
      // Перезагружаем страницу, чтобы заново пройти авторизацию
      setTimeout(() => {
        window.location.reload();
      }, 500);
    }
    return Promise.reject(error);
  }
);

export function setCookie(name: string, value: string, days = 7) {
  console.log('🍪 [Cookie] Устанавливаем:', name);
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
  console.log('✅ [Cookie] Установлено. Текущие cookie:', document.cookie);
}

export function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  const result = match ? match[2] : null;
  console.log('🔍 [Cookie] Поиск', name, ':', result ? 'НАЙДЕН' : 'НЕ НАЙДЕН');
  return result;
}

export function deleteCookie(name: string) {
  console.log('🗑️ [Cookie] Удаляем:', name);
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
  console.log('✅ [Cookie] Удалено. Текущие cookie:', document.cookie);
}

export default api;