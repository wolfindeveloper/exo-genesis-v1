// client/src/utils/telegram.ts
/**
 * Возвращает заголовки для авторизации через Telegram initData
 */
export function withTelegramAuth(): Record<string, string> {
  // Проверяем, что код выполняется в Telegram WebApp
  if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
    const tg = (window as any).Telegram.WebApp
    const initData = tg.initData || ''
    
    if (initData) {
      return { 'X-Telegram-Init-Data': initData }
    }
  }
  
  // Если не в Telegram или нет initData — возвращаем пустые заголовки
  return {}
}

/**
 * Проверяет, что приложение запущено внутри Telegram
 */
export function isTelegramWebApp(): boolean {
  return typeof window !== 'undefined' && !!(window as any).Telegram?.WebApp
}

/**
 * Инициализирует Telegram WebApp (расширяет на весь экран, включает кнопку закрытия)
 */
export function initTelegramWebApp(): void {
  if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
    const tg = (window as any).Telegram.WebApp
    tg.expand() // Раскрыть на весь экран
    tg.enableClosingConfirmation() // Показать подтверждение закрытия
    tg.ready() // Сообщить Telegram, что приложение готово
  }
}