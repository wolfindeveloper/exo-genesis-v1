// client/src/utils/telegram.ts
import WebApp from '@twa-dev/sdk'

export function getTelegramInitData(): string | null {
  // Безопасная проверка: есть ли initData от Telegram
  if (typeof window === 'undefined' || !WebApp.initData) {
    return null
  }
  return WebApp.initData
}

export function withTelegramAuth(headers: Record<string, string> = {}): Record<string, string> {
  const initData = getTelegramInitData()
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
  }
  return headers
}