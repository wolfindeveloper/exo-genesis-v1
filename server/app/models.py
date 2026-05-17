# server/app/models.py
import enum
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Boolean, JSON, ForeignKey, Enum as SAEnum, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 🔥 Обновлённый enum под сервис
class ExpeditionStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"
    CLAIMED = "claimed"

class Player(Base):
    __tablename__ = "players"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64))
    xgen_balance = Column(Float, default=100.0)  # Float для дробных наград
    xp = Column(Integer, default=0)
    pilot_rank = Column(String(16), default="Rookie")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    ships = relationship("Ship", back_populates="player", cascade="all, delete-orphan")
    expeditions = relationship("Expedition", back_populates="player")
    artifacts = relationship("Artifact", back_populates="player")

class Ship(Base):
    __tablename__ = "ships"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(64), default="STELLA")
    tier = Column(Integer, default=1)  # Переименовал rank → tier для консистентности
    materia = Column(Integer, default=1250)
    speed = Column(Integer, default=85)
    status = Column(String(16), default="Active")
    is_active = Column(Boolean, default=True)  # Для блокировки уничтоженных кораблей
    
    # 🔥 Поля под расчёт урона в сервисе
    base_armor = Column(Float, default=0.15)  # 0.0–0.95
    max_hp = Column(Integer, default=1000)
    hp = Column(Integer, default=1000)  # Текущее здоровье
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    player = relationship("Player", back_populates="ships")
    expeditions = relationship("Expedition", back_populates="ship")

class Expedition(Base):
    __tablename__ = "expeditions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    ship_id = Column(PG_UUID(as_uuid=True), ForeignKey("ships.id", ondelete="CASCADE"), nullable=False)
    
    # 🔥 Поля под сервис
    zone_config_id = Column(String(64), nullable=False)
    zone_risk = Column(Float, nullable=False)  # 0.0–100.0
    duration_seconds = Column(Integer, nullable=False)
    
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    status = Column(SAEnum(ExpeditionStatus), default=ExpeditionStatus.IN_PROGRESS, nullable=False)
    
    # Результаты
    loot_resources = Column(JSON, default=dict)  # {"fuel_scrap": 10, "metal_alloy": 5}
    loot_rare = Column(JSON, default=list)       # ["dark_matter_shard"]
    damage_taken = Column(Integer, default=0)
    is_destroyed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    player = relationship("Player", back_populates="expeditions")
    ship = relationship("Ship", back_populates="expeditions")

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64))
    rarity = Column(String(16), default="common")
    effect = Column(JSON, default=dict)
    cycles_remaining = Column(Integer, default=30)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    player = relationship("Player", back_populates="artifacts")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_hash = Column(String(64), unique=True, nullable=False)
    artifact_id = Column(PG_UUID(as_uuid=True), ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False)
    discoverer_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))