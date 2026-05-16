# server/app/services/crafting.py
import yaml
import random
import json
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Artifact, Player

_artifacts_cache = None

def load_artifacts_config() -> list:
    global _artifacts_cache
    if _artifacts_cache is None:
        current = Path(__file__).resolve()
        for _ in range(5):
            candidate = current.parent / "data"
            if candidate.exists() and (candidate / "artifacts.yaml").exists():
                with open(candidate / "artifacts.yaml", "r", encoding="utf-8") as f:
                    _artifacts_cache = yaml.safe_load(f) or []
                break
            current = current.parent
            if current.parent == current:
                break
    return _artifacts_cache or []

def weighted_random_choice(items: list) -> dict:
    total_weight = sum(item.get("weight", 1) for item in items)
    r = random.uniform(0, total_weight)
    cumulative = 0
    for item in items:
        cumulative += item.get("weight", 1)
        if r <= cumulative:
            return item
    return items[-1]

async def perform_craft(db: AsyncSession, player_id: int, cooldown_sec: int = 10) -> dict:
    # 🔒 Атомарная блокировка строки игрока (предотвращает race conditions)
    result = await db.execute(
        select(Player).where(Player.id == player_id).with_for_update()
    )
    player = result.scalar_one_or_none()
    if not player:
        raise ValueError("Player not found")

    # ⏱ Проверка кулдауна
    now = datetime.now(timezone.utc)
    if player.last_craft_at and (now - player.last_craft_at).total_seconds() < cooldown_sec:
        remaining = cooldown_sec - (now - player.last_craft_at).total_seconds()
        raise ValueError(f"Cooldown active. Wait {int(remaining)}s")

    # 🎲 Выбор артефакта
    artifacts = load_artifacts_config()
    if not artifacts:
        raise ValueError("Artifacts config empty")
    
    chosen = weighted_random_choice(artifacts)
    
    # 📦 Создание записи + обновление таймстампа
    new_artifact = Artifact(
        player_id=player_id,
        config_id=chosen["id"],
        name_ru=chosen["name_ru"],
        name_en=chosen["name_en"],
        rarity=chosen["rarity"],
        effect_json=json.dumps(chosen.get("effect_json", {})),
        is_equipped=False
    )
    
    db.add(new_artifact)
    player.last_craft_at = now  # 👈 Атомарное обновление в той же транзакции
    
    await db.commit()  # Фиксируется только если всё прошло успешно
    await db.refresh(new_artifact)
    
    return {
        "artifact_id": new_artifact.id,
        "config_id": chosen["id"],
        "name_ru": chosen["name_ru"],
        "name_en": chosen["name_en"],
        "rarity": chosen["rarity"],
        "effect": json.loads(chosen.get("effect_json", "{}"))
    }