"""add game columns: xp, pilot_rank, ships, expeditions

Revision ID: 20260517
Revises: <предыдущий_ревизия_если_есть>
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
import uuid

# revision identifiers
revision = '20260517'
down_revision = None  # или ID предыдущей миграции
branch_labels = None
depends_on = None

# Создаём enum для статусов экспедиций
expedition_status = sa.Enum('pending', 'active', 'completed', 'claimed', name='expeditionstatus')

def upgrade():
    # === Сначала проверяем тип id в artifacts ===
    # Если artifacts.id — INTEGER, меняем его на UUID
    # (Это безопасно на ранней стадии, если таблица пустая или тестовая)
    
    # 1. Меняем тип id в artifacts на UUID (если нужно)
    op.alter_column('artifacts', 'id',
                   type_=sa.UUID(as_uuid=True),
                   postgresql_using='id::uuid')
    
    # 2. Добавляем колонки в players
    op.add_column('players', sa.Column('xp', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('players', sa.Column('pilot_rank', sa.String(length=16), nullable=True, server_default='Rookie'))
    
    # 3. Создаём таблицу ships
    op.create_table('ships',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True, default='STELLA'),
        sa.Column('rank', sa.Integer(), nullable=True, default=1),
        sa.Column('materia', sa.Integer(), nullable=True, default=1250),
        sa.Column('speed', sa.Integer(), nullable=True, default=85),
        sa.Column('status', sa.String(length=16), nullable=True, default='Active'),
        sa.Column('health_max', sa.Integer(), nullable=True, default=1000),
        sa.Column('health_current', sa.Integer(), nullable=True, default=1000),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_ships_player_id'), 'ships', ['player_id'], unique=False)
    
    # 4. Создаём enum для экспедиций
    expedition_status = sa.Enum('pending', 'active', 'completed', 'claimed', name='expeditionstatus')
    expedition_status.create(op.get_bind())
    
    # 5. Создаём таблицу expeditions
    op.create_table('expeditions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ship_id', sa.UUID(as_uuid=True), sa.ForeignKey('ships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', expedition_status, nullable=True, default='pending'),
        sa.Column('tier', sa.Integer(), nullable=True, default=1),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, default=60),
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('loot', sa.JSON(), nullable=True, default=dict),
        sa.Column('damage_taken', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_expeditions_player_id'), 'expeditions', ['player_id'], unique=False)
    
    # 6. Создаём таблицу recipes с UUID foreign keys
    op.create_table('recipes',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('recipe_hash', sa.String(length=64), unique=True, nullable=False),
        sa.Column('artifact_id', sa.UUID(as_uuid=True), sa.ForeignKey('artifacts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('discoverer_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_recipes_artifact_id'), 'recipes', ['artifact_id'], unique=False)

def downgrade():
    # Откат в обратном порядке
    op.drop_index(op.f('ix_expeditions_player_id'), table_name='expeditions')
    op.drop_table('expeditions')
    expedition_status.drop(op.get_bind())
    
    op.drop_index(op.f('ix_ships_player_id'), table_name='ships')
    op.drop_table('ships')
    
    op.drop_column('players', 'pilot_rank')
    op.drop_column('players', 'xp')