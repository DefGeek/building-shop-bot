import { useEffect, useState } from 'react';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
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

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export function useTelegram() {
  const [tg, setTg] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isInTelegram, setIsInTelegram] = useState(false);

  useEffect(() => {
    const telegram = window.Telegram?.WebApp;
    if (telegram) {
      setTg(telegram);
      telegram.ready();
      telegram.expand();
      setUser(telegram.initDataUnsafe?.user || null);
      setIsInTelegram(true);
      
      // ⚠️ ВАЖНО: Сохраняем initData в localStorage, чтобы он не терялся при навигации
      if (telegram.initData) {
        localStorage.setItem('tg_init_data', telegram.initData);
        console.log('💾 [Telegram] initData сохранен в localStorage');
      }
    } else {
      setIsInTelegram(false);
    }
  }, []);

  return { tg, user, isInTelegram };
}
