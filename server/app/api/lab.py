# server/app/api/lab.py
import json
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import Player
from app.services.crafting import perform_craft
from app.utils.telegram import validate_telegram_init_data
from app.core.config import settings

router = APIRouter(prefix="/api/lab", tags=["lab"])

@router.post("/craft")
async def craft_artifact(
    x_telegram_init_data: str = Header(default=""),
    db: AsyncSession = Depends(get_db)
):
    # 🔐 Валидация данных от Telegram
    validated_data = validate_telegram_init_data(x_telegram_init_data, settings.TELEGRAM_BOT_TOKEN)
    if not validated_data:
        raise HTTPException(401, detail="Invalid or missing Telegram initData")

    user_json = validated_data.get("user", "{}")
    user_data = json.loads(user_json)
    user_id = user_data.get("id")

    if not user_id:
        raise HTTPException(400, detail="User ID not found in initData")

    # 🔍 Находим или создаём игрока по telegram_id
    result = await db.execute(select(Player).where(Player.telegram_id == str(user_id)))
    player = result.scalar_one_or_none()

    if not player:
        username = user_data.get("username", f"user_{user_id}")
        player = Player(telegram_id=str(user_id), username=username, xgen_balance=100.0)
        db.add(player)
        await db.commit()
        await db.refresh(player)

    try:
        return await perform_craft(db, player.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))