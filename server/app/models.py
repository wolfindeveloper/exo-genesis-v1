# server/app/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64))
    xgen_balance = Column(Integer, default=100) # Начальный баланс
    xp = Column(Integer, default=0)
    pilot_rank = Column(String(16), default="Rookie")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    ships = relationship("Ship", back_populates="player", cascade="all, delete-orphan")
    expeditions = relationship("Expedition", back_populates="player")

class Ship(Base):
    __tablename__ = "ships"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    
    # Данные из дизайна
    name = Column(String(64), default="STELLA")
    rank = Column(Integer, default=1) # 1-5
    materia = Column(Integer, default=1250)
    speed = Column(Integer, default=85)
    status = Column(String(16), default="Active") # Active, InExpedition, Repaired
    
    # HP Bar
    health_max = Column(Integer, default=1000)
    health_current = Column(Integer, default=1000)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="ships")
    expeditions = relationship("Expedition", back_populates="ship")

class Expedition(Base):
    __tablename__ = "expeditions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    ship_id = Column(PG_UUID(as_uuid=True), ForeignKey("ships.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(16), default="pending") # pending, active, completed, claimed
    tier = Column(Integer, default=1) # Сложность
    duration_minutes = Column(Integer, default=60) # Сколько длится
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True) # Когда закончится
    
    # Лут и урон (пока заглушки)
    loot = Column(JSON, default=dict) 
    damage_taken = Column(Integer, default=0)
    
    player = relationship("Player", back_populates="expeditions")
    ship = relationship("Ship", back_populates="expeditions")