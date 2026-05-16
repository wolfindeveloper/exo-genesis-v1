# server/app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class ExpeditionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String)
    xgen_balance = Column(Float, default=0.0)
    last_craft_at = Column(DateTime(timezone=True), nullable=True)  # Защита от race conditions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    ships = relationship("Ship", back_populates="player")
    expeditions = relationship("Expedition", back_populates="player")
    artifacts = relationship("Artifact", back_populates="player")

class Ship(Base):
    __tablename__ = "ships"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    config_id = Column(String, nullable=False)  # ссылается на ships.yaml:id
    tier = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    base_armor = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    player = relationship("Player", back_populates="ships")
    expeditions = relationship("Expedition", back_populates="ship")

class Expedition(Base):
    __tablename__ = "expeditions"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    zone_config_id = Column(String, nullable=False)  # ссылается на zones.yaml:id
    zone_risk = Column(Float, nullable=False)  # snapshot риска на момент старта
    duration_seconds = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(ExpeditionStatus), default=ExpeditionStatus.PENDING)
    
    # Результаты
    loot_resources = Column(String)  # JSON: {"fuel_scrap": 10, "metal_alloy": 5}
    loot_rare = Column(String)  # JSON: ["dark_matter_shard"]
    damage_taken = Column(Integer, default=0)
    is_destroyed = Column(Boolean, default=False)
    
    player = relationship("Player", back_populates="expeditions")
    ship = relationship("Ship", back_populates="expeditions")


class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    config_id = Column(String, nullable=False)  # ссылается на artifacts.yaml:id
    name_ru = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    rarity = Column(String, nullable=False)  # "common", "rare", "legendary"
    effect_json = Column(String)  # JSON: {"damage_boost": 0.1}
    crafted_at = Column(DateTime(timezone=True), server_default=func.now())
    is_equipped = Column(Boolean, default=False)
    
    player = relationship("Player", back_populates="artifacts")