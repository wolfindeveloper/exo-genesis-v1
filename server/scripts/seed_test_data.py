# server/scripts/seed_test_data.py
# === FIX: Добавляем корень проекта в sys.path ===
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# ================================================

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.models import Base, Player, Ship
from app.core.config import settings

async def seed():
    # Создаём async engine
    engine = create_async_engine(settings.DATABASE_URL)
    
    # Создаём таблицы, если нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаём сессию
    async with AsyncSession(engine) as db:
        # === Создаём/находим игрока ===
        result = await db.execute(select(Player).where(Player.telegram_id == "test_123"))
        player = result.scalar_one_or_none()
        
        if not player:
            player = Player(telegram_id="test_123", username="TestPilot", xgen_balance=100.0)
            db.add(player)
            await db.commit()
            await db.refresh(player)  # 👈 Загружаем сгенерированный id
            print(f"✅ Created player: id={player.id}")
        else:
            print(f"✅ Player exists: id={player.id}")
        
        # === Создаём/находим корабль ===
        result = await db.execute(
            select(Ship).where(Ship.player_id == player.id, Ship.config_id == "ship_t1")
        )
        ship = result.scalar_one_or_none()
        
        if not ship:
            ship = Ship(
                player_id=player.id,
                config_id="ship_t1",
                tier=1,
                hp=100,
                max_hp=100,
                base_armor=0.05,
                is_active=True
            )
            db.add(ship)
            await db.commit()
            await db.refresh(ship)  # 👈 КРИТИЧНО: загружаем id после insert
            print(f"✅ Created ship: id={ship.id}")
        else:
            print(f"✅ Ship exists: id={ship.id}")
        
        print(f"\n📋 Test credentials:\n  player_id={player.id}\n  ship_id={ship.id}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())