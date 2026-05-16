# server/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path
import re

# === Добавляем корень проекта в PATH ===
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Импортируем настройки и модели
from app.core.config import settings
from app.models import Base

# Alembic Config
config = context.config

# === КОНВЕРТАЦИЯ asyncpg → psycopg2 для миграций ===
def convert_async_url_to_sync(async_url: str) -> str:
    """Заменяет postgresql+asyncpg:// на postgresql:// для синхронных миграций"""
    return re.sub(r'^postgresql\+asyncpg://', 'postgresql://', async_url)

sync_database_url = convert_async_url_to_sync(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_database_url)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()