# server/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

# === Надёжный способ найти корень проекта ===
# Ищем .env, поднимаясь вверх по дереву папок
def find_project_root() -> Path:
    current = Path(__file__).resolve()
    # Поднимаемся максимум на 5 уровней вверх
    for _ in range(5):
        if (current / ".env").exists():
            return current
        parent = current.parent
        if parent == current:  # достигли корня диска
            break
        current = parent
    # Fallback: текущая рабочая директория
    return Path.cwd()

PROJECT_ROOT = find_project_root()
ENV_FILE = PROJECT_ROOT / ".env"

# Для отладки (можно закомментировать после фикса)
print(f"🔍 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"🔍 ENV_FILE: {ENV_FILE}")
print(f"🔍 .env exists: {ENV_FILE.exists()}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # === Обязательные поля ===
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    SECRET_KEY: str
    TELEGRAM_WEBAPP_URL: str = "https://your-app.tonkeeper.com"
    
    # === Опциональные с дефолтами ===
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    CACHE_TTL_SECONDS: int = 300

settings = Settings()