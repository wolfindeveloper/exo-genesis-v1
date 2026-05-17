# server/app/models.py
import enum
import uuid
from datetime import datetime  # ← только datetime, без timezone!
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Boolean, JSON, ForeignKey, Enum as SAEnum, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
    xgen_balance = Column(Float, default=100.0)
    xp = Column(Integer, default=0)
    pilot_rank = Column(String(16), default="Rookie")
    created_at = Column(DateTime, default=datetime.utcnow)  # ← naive
    
    ships = relationship("Ship", back_populates="player", cascade="all, delete-orphan")
    expeditions = relationship("Expedition", back_populates="player")
    artifacts = relationship("Artifact", back_populates="player")

class Ship(Base):
    __tablename__ = "ships"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(64), default="STELLA")
    tier = Column(Integer, default=1)
    materia = Column(Integer, default=1250)
    speed = Column(Integer, default=85)
    status = Column(String(16), default="Active")
    is_active = Column(Boolean, default=True)
    
    base_armor = Column(Float, default=0.15)
    max_hp = Column(Integer, default=1000)
    hp = Column(Integer, default=1000)
    
    created_at = Column(DateTime, default=datetime.utcnow)  # ← naive
    
    player = relationship("Player", back_populates="ships")
    expeditions = relationship("Expedition", back_populates="ship")

class Expedition(Base):
    __tablename__ = "expeditions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    ship_id = Column(PG_UUID(as_uuid=True), ForeignKey("ships.id", ondelete="CASCADE"), nullable=False)
    
    zone_config_id = Column(String(64), nullable=False)
    zone_risk = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    
    # ← Все datetime naive (без timezone)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    status = Column(SAEnum(ExpeditionStatus), default=ExpeditionStatus.IN_PROGRESS, nullable=False)
    
    loot_resources = Column(JSON, default=dict)
    loot_rare = Column(JSON, default=list)
    damage_taken = Column(Integer, default=0)
    is_destroyed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)  # ← naive
    
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
    created_at = Column(DateTime, default=datetime.utcnow)  # ← naive
    
    player = relationship("Player", back_populates="artifacts")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_hash = Column(String(64), unique=True, nullable=False)
    artifact_id = Column(PG_UUID(as_uuid=True), ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False)
    discoverer_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # ← naive