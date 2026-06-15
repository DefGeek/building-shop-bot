import { useEffect, useState } from 'react';


// TypeScript по умолчанию не знает, что такое объект Telegram.
// Эти интерфейсы дают компилятору
// "инструкцию": "Если я обращаюсь к user.first_name, там гарантированно будет строка, а не число".
// Это защищает от ошибок.
interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string; // ? означает, что поле необязательное
  username?: string;
  language_code?: string;
}

//interface новый тип который существует только в этом файле
interface TelegramWebApp {
  initData: string; // hmac от телеграм с данными пользователя направляет на бэк для верификации
  initDataUnsafe: {  // распарсенные данные пользователя
    user?: TelegramUser;
  };
  ready: () => void; // Функция: сообщить Telegram, что приложение готово
  expand: () => void; // Функция: развернуть приложение на всю высоту
  MainButton: {
    text: string;
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
  };
}

// declare global поскольку переписываем уже существубщий глобальный тип window
declare global {
  interface Window {
    // это означает добавить свойство Telegram к Window
    // вопрос означает,что оно может отсутствовать если мы не в тг
    Telegram?: {
      // это означает,что внутри будет объект WebApp типа TelegramWebApp
      // который описан выше
      // т.е. Window.Telegram.WebApp
      WebApp: TelegramWebApp;
    };
  }
}

//export делает функцию доступной в других файлах
export function useTelegram() {
  // через useState компонент React знает, что при вызове setTg
  // ему нужно запустить его (компонент) заново
  const [tg, setTg] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isInTelegram, setIsInTelegram] = useState(false);

  useEffect(() => {
    // если мы в тг тоо объект WebApp извлечётся
    // если через браузер то нет
    const telegram = window.Telegram?.WebApp;
    if (telegram) {
      setTg(telegram);
      // убираем спинер загрузки,т.к. объект WebApp загрузился
      telegram.ready();
      // окно растягивается на весь экран
      telegram.expand();
      //достаём данные из необезопасного объекта и ставим флаг
      //что мы в тг
      setUser(telegram.initDataUnsafe?.user || null);
      setIsInTelegram(true);

      // если поступили данные юзера + HASH от теге то
      // сорханяем их в данных браузера, дальше направим это на
      // бэкенд для проверки
      // если просто окрыли браузер не в тг то просто ставим флаг false
      if (telegram.initData) {
        localStorage.setItem('tg_init_data', telegram.initData);
      }
    } else {
      setIsInTelegram(false);
    }
  }, []); // Пустой массив означает: выполнить этот код ТОЛЬКО ОДИН РАЗ при монтировании компонента

  return { tg, user, isInTelegram };
}
