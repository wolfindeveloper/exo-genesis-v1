# server/app/api/hangar.py
import json
import urllib.parse
from datetime import datetime
from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import Player, Ship, Expedition, ExpeditionStatus

router = APIRouter(prefix="/api/hangar", tags=["hangar"])

def parse_init_data(init_data: str) -> dict:
    parsed = dict(urllib.parse.parse_qsl(init_data))
    return json.loads(parsed.get("user", "{}"))

@router.get("/status")
async def get_hangar_status(
    init_data: str = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    if not init_data:
        raise HTTPException(401, "Missing initData")
    
    user = parse_init_data(init_data)
    telegram_id = user.get("id")
    username = user.get("username", "Commander")

    # Поиск или создание игрока
    result = await db.execute(select(Player).where(Player.telegram_id == telegram_id))
    player = result.scalar_one_or_none()
    
    if not player:
        player = Player(telegram_id=telegram_id, username=username, xgen_balance=1000, xp=0)
        db.add(player)
        await db.flush()
        ship = Ship(player_id=player.id, name="STELLA", rank=1, materia=1250, speed=85, status="Active", health_max=1000, health_current=1000)
        db.add(ship)
        await db.commit()
        await db.refresh(player)
        await db.refresh(ship)
    else:
        ship_res = await db.execute(select(Ship).where(Ship.player_id == player.id).limit(1))
        ship = ship_res.scalar_one_or_none()

    # Проверка активной экспедиции (под новый enum и поля)
    exp_res = await db.execute(select(Expedition).where(
        Expedition.player_id == player.id,
        Expedition.ship_id == ship.id,
        Expedition.status == ExpeditionStatus.IN_PROGRESS
    ))
    active_exp = exp_res.scalar_one_or_none()
    
    action_type = "ready"
    action_text = "⚡ TAP TO MINE ⚡"
    timer_seconds = 0

    if active_exp and active_exp.end_time:
        now = datetime.utcnow()
        if now < active_exp.end_time:
            action_type = "expedition"
            diff = int((active_exp.end_time - now).total_seconds())
            action_text = f"🚀 RETURNING IN {diff}s"
            timer_seconds = diff
        else:
            action_type = "claim"
            action_text = "🎁 CLAIM LOOT"

    return {
        "player": {
            "username": player.username or "Commander",
            "xgen_balance": player.xgen_balance,
            "xp": player.xp,
            "level": 1 + (player.xp // 1000),
            "xp_to_next": 1000
        },
        "ship": {
            "name": ship.name,
            "rank": ship.rank,
            "materia": ship.materia,
            "speed": ship.speed,
            "status": ship.status,
            "hp_current": ship.health_current,
            "hp_max": ship.health_max,
            "boosts": ["+12% Scan Range", "+5% Speed"]
        },
        "action": {
            "type": action_type,
            "text": action_text,
            "timer_seconds": timer_seconds
        }
    }