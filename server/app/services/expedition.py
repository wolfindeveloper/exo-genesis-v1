# server/app/services/expedition.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Expedition, ExpeditionStatus, Ship, Player
import random
import json

def calculate_damage(zone_risk: float, ship_armor: float, artifact_debuff: float = 1.0) -> float:
    base_chance = zone_risk / 100.0
    armor_factor = 1.0 - min(ship_armor, 0.95)
    return base_chance * armor_factor * artifact_debuff

def calculate_loot(zone_risk: float, duration_min: int, ship_tier: int) -> dict:
    base = 1 + (zone_risk / 100) + (duration_min / 60) + (ship_tier * 0.1)
    return {
        "fuel_scrap": max(5, int(10 * base)),
        "metal_alloy": max(2, int(5 * base * random.uniform(0.8, 1.2))),
    }

async def start_expedition(
    db: AsyncSession,
    player_id: int,
    ship_id: int,
    zone_config_id: str,
    zone_risk: float,
    duration_min: int
) -> Expedition:
    now = datetime.utcnow()
    end_time = now + timedelta(minutes=duration_min)
    
    expedition = Expedition(
        player_id=player_id,
        ship_id=ship_id,
        zone_config_id=zone_config_id,
        zone_risk=zone_risk,
        duration_seconds=duration_min * 60,
        end_time=end_time,
        status=ExpeditionStatus.IN_PROGRESS,
    )
    db.add(expedition)
    await db.commit()
    await db.refresh(expedition)
    return expedition

async def claim_expedition(
    db: AsyncSession,
    expedition_id: int,
    anti_cheat_max_drift_seconds: int = 5
) -> dict:
    result = await db.execute(select(Expedition).where(Expedition.id == expedition_id))
    expedition = result.scalar_one_or_none()
    if not expedition:
        raise ValueError("Expedition not found")
    
    if expedition.status != ExpeditionStatus.IN_PROGRESS:
        raise ValueError(f"Invalid status: {expedition.status.value}")
    
    now = datetime.utcnow()
    
    # 🔹 ПЕРВЫМ ДЕЛОМ: если экспедиция ещё не завершена — просто верни прогресс
    if now < expedition.end_time:
        total = expedition.duration_seconds
        elapsed = (now - expedition.start_time).total_seconds()
        return {
            "status": "in_progress",
            "progress": min(1.0, elapsed / total),
            "seconds_remaining": max(0, int((expedition.end_time - now).total_seconds())),
        }
    
    # 🔹 ТОЛЬКО ПОСЛЕ завершения: анти-чит проверка
    # time_drift = abs((now - expedition.end_time).total_seconds())
    # if time_drift > anti_cheat_max_drift_seconds:
    #     raise ValueError("Invalid timestamp (possible time travel)")
    
    # === Экспедиция завершена: считаем результаты ===
    ship_result = await db.execute(select(Ship).where(Ship.id == expedition.ship_id))
    ship = ship_result.scalar_one()
    
    damage_ratio = calculate_damage(expedition.zone_risk, ship.base_armor)
    damage = int(ship.max_hp * damage_ratio * random.uniform(0.8, 1.2))
    
    if damage >= ship.hp:
        expedition.status = ExpeditionStatus.DESTROYED
        expedition.is_destroyed = True
        ship.is_active = False
        loot, rare = {}, []
    elif damage > ship.hp * 0.5:
        expedition.status = ExpeditionStatus.DAMAGED
        ship.hp -= damage
        loot = calculate_loot(expedition.zone_risk, expedition.duration_seconds // 60, ship.tier)
        rare = ["dark_matter_shard"] if random.random() < 0.1 else []
    else:
        expedition.status = ExpeditionStatus.COMPLETED
        ship.hp -= damage
        loot = calculate_loot(expedition.zone_risk, expedition.duration_seconds // 60, ship.tier)
        rare = ["dark_matter_shard"] if random.random() < 0.15 else []
    
    expedition.damage_taken = damage
    expedition.loot_resources = json.dumps(loot)
    expedition.loot_rare = json.dumps(rare)
    
    player_result = await db.execute(select(Player).where(Player.id == expedition.player_id))
    player = player_result.scalar_one()
    xgen_reward = sum(loot.values()) * 0.1 + len(rare) * 10.0
    player.xgen_balance += xgen_reward
    
    await db.commit()
    
    return {
        "status": expedition.status.value,
        "loot": loot,
        "rare": rare,
        "xgen_earned": xgen_reward,
        "ship_hp": ship.hp,
        "ship_destroyed": expedition.is_destroyed,
    }