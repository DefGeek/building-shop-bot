// Импортируем два хука из React.
import { useEffect, useState } from 'react';


//Это описание формы объекта. Мы говорим TypeScript: "Объект пользователя должен выглядеть вот так".
interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string; //знак вопрос означает опциональность
  username?: string;
  language_code?: string;
}

interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: TelegramUser;
  };
  ready: () => void;
  expand: () => void;
  MainButton: {
    text: string;
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
  };
}


//говорим TypeScript что телеграм в объект Window
// страницы добавляет поле Telegram (window.Telegram)
declare global {
  interface Window {
    //так как window.Telegram может отсутствовать если
    //открыть приложение через браузер а не через телеграм
    //то ставим знак вопроса
    Telegram?: {
      //WebApp — поле внутри объекта Telegram
      //: TelegramWebApp - тип этого поля
      WebApp: TelegramWebApp;
    };
  }
}

// в React есть правило,что если функция использует внутри стандартные
// useState и useEffect и её название начинается с
export function useTelegram() {
  //Когда пользователь открывает Mini App, он делает это внутри
  //встроенного браузера Телеграма. Телеграм "впрыскивает" на страницу
  //специальный объект с данными и инструментами
  //useTelegram берёт эти данные и проверяет находимся ли мы в браузере от тг или просто браузере
  //Собирает данные пользователя и отдаёт React компоненту
  //говорит тг о том что приложение готово к работе Ready и expand расширь экран


  // через useState мы говорим что переменная может быть
  // либо TelegramWebApp либо null и в самом
  // начале через скобки её задаём как null

  //в React есть концепция реактивности. Компонент - это функция
  //которая возвращает разметку JSX. React вызывает эту функцию каждый
  // раз когда меняются данные (состояние)
  // к примеру  - tg не обычная переменная, а значение их состояния React
  //React будет за ней следить,  а за обычной следить не будет
  //поэтому tg=new_value не сработает
  const [tg, setTg] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isInTelegram, setIsInTelegram] = useState(false);

  // хук который выполняет код после того как компонент появится на экране
  useEffect(() => {
    const telegram = window.Telegram?.WebApp;
    if (telegram) {
      setTg(telegram);
      //по требованию telegram sdk обязаны сообщить что приложение готово
      telegram.ready();
      //расширяем mini app на весь экран
      telegram.expand();
      setUser(telegram.initDataUnsafe?.user || null);
      setIsInTelegram(true);
    } else {
      setIsInTelegram(false);
    }
  }, []); //Пустой массив [] в конце означает: "Выполни этот код только один раз, когда компонент загрузится".

  return { tg, user, isInTelegram };
}