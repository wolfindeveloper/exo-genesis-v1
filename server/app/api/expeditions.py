# server/app/api/expeditions.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.db import get_db
from app.models import Player, Ship, Expedition, ExpeditionStatus
from app.services.expedition import start_expedition, claim_expedition
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/expeditions", tags=["expeditions"])

class StartExpeditionRequest(BaseModel):
    ship_id: int
    zone_config_id: str = Field(..., min_length=1)
    duration_min: int = Field(..., ge=1, le=240)
    zone_risk: float = Field(..., ge=0, le=100)

@router.post("/start")
async def start(
    req: StartExpeditionRequest,
    db: AsyncSession = Depends(get_db),
    x_telegram_init_data: str = Header(default="dummy")
):
    result = await db.execute(select(Player).limit(1))
    player = result.scalar_one_or_none()
    
    if not player:
        player = Player(telegram_id="test_123", username="TestPilot", xgen_balance=100.0)
        db.add(player)
        await db.commit()
        await db.refresh(player)
    
    ship_result = await db.execute(
        select(Ship).where(
            Ship.id == req.ship_id,
            Ship.player_id == player.id,
            Ship.is_active == True
        )
    )
    ship = ship_result.scalar_one_or_none()
    if not ship:
        raise HTTPException(400, detail="Ship not found or inactive")
    
    expedition = await start_expedition(
        db=db,
        player_id=player.id,
        ship_id=ship.id,
        zone_config_id=req.zone_config_id,
        zone_risk=req.zone_risk,
        duration_min=req.duration_min
    )
    
    return {
        "expedition_id": expedition.id,
        "status": "in_progress",
        "end_time": expedition.end_time.isoformat(),
    }

@router.get("/{expedition_id}/status")
async def status(expedition_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Expedition).where(Expedition.id == expedition_id))
    expedition = result.scalar_one_or_none()
    if not expedition:
        raise HTTPException(404, detail="Expedition not found")
    
    now = datetime.now(timezone.utc)
    if expedition.status == ExpeditionStatus.IN_PROGRESS and now < expedition.end_time:
        total = expedition.duration_seconds
        elapsed = (now - expedition.start_time).total_seconds()
        progress = min(1.0, max(0.0, elapsed / total))
        remaining = max(0, int((expedition.end_time - now).total_seconds()))
        return {
            "status": "in_progress",
            "progress": round(progress, 3),
            "seconds_remaining": remaining,
        }
    return {"status": expedition.status.value, "completed": True}

@router.post("/{expedition_id}/claim")
async def claim(expedition_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await claim_expedition(db, expedition_id)
        return result
    except ValueError as e:
        raise HTTPException(400, detail=str(e))