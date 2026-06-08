import axios from 'axios'; //axios - библиотека для отправки http запросов

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// перехватчик срабатывает при каждом HTTP запросе к backend
// берёт jwt токен из локального хранилища и отправляет его на backend
// для проверки авторизован ли пользователь
api.interceptors.request.use((config) => {
  //jwt токен
  const token = localStorage.getItem('access_token'); достаёт токен из localStorage браузера
  //если токен есть то добавляем его в заголовок Authorization
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок авторизации
//interceptor - перехватчик
api.interceptors.response.use(
  (response) => response,
  (error) => {
    //если пришла ошибка 401 то значит у пользователя
    //либо нет доступа либо токен невалиден или просрочен
    if (error.response?.status === 401) {
      //удаляем старый токен
      localStorage.removeItem('access_token');
      //обновляем страницу, чтобы авторизация началась заново
      window.location.reload();
    }
    //передаём ошибку дальше, чтоб можно было с ней сделать что то ещё
    return Promise.reject(error);
  }
);

//экспорт настроенного axios чтобы другие файлы могли его использовать
export default api;
