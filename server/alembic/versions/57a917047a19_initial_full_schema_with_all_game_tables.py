"""initial full schema with all game tables

Revision ID: 57a917047a19
Revises: 
Create Date: 2026-05-17 13:05:55.611127
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

revision: str = '57a917047a19'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Players
    op.create_table('players',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), unique=True, nullable=False, index=True),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('xgen_balance', sa.Integer(), nullable=True, server_default=sa.text('100')),
        sa.Column('xp', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('pilot_rank', sa.String(length=16), nullable=True, server_default=sa.text("'Rookie'")),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )

    # 2. Ships
    op.create_table('ships',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True, server_default=sa.text("'STELLA'")),
        sa.Column('rank', sa.Integer(), nullable=True, server_default=sa.text('1')),
        sa.Column('materia', sa.Integer(), nullable=True, server_default=sa.text('1250')),
        sa.Column('speed', sa.Integer(), nullable=True, server_default=sa.text('85')),
        sa.Column('status', sa.String(length=16), nullable=True, server_default=sa.text("'Active'")),
        sa.Column('health_max', sa.Integer(), nullable=True, server_default=sa.text('1000')),
        sa.Column('health_current', sa.Integer(), nullable=True, server_default=sa.text('1000')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_ships_player_id'), 'ships', ['player_id'], unique=False)

    # 3. Expedition Status Enum
    expedition_status = PG_ENUM('pending', 'active', 'completed', 'claimed', name='expeditionstatus', create_type=False)
    # expedition_status.create(op.get_bind())

    # 4. Expeditions
    op.create_table('expeditions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ship_id', sa.UUID(as_uuid=True), sa.ForeignKey('ships.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', expedition_status, nullable=True, server_default=sa.text("'pending'")),
        sa.Column('tier', sa.Integer(), nullable=True, server_default=sa.text('1')),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, server_default=sa.text('60')),
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('loot', sa.JSON(), nullable=True, server_default=sa.text("'{}'::json")),
        sa.Column('damage_taken', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_expeditions_player_id'), 'expeditions', ['player_id'], unique=False)

    # 5. Artifacts
    op.create_table('artifacts',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('rarity', sa.String(length=16), nullable=True, server_default=sa.text("'common'")),
        sa.Column('effect', sa.JSON(), nullable=True, server_default=sa.text("'{}'::json")),
        sa.Column('cycles_remaining', sa.Integer(), nullable=True, server_default=sa.text('30')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_artifacts_player_id'), 'artifacts', ['player_id'], unique=False)

    # 6. Recipes
    op.create_table('recipes',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('recipe_hash', sa.String(length=64), unique=True, nullable=False),
        sa.Column('artifact_id', sa.UUID(as_uuid=True), sa.ForeignKey('artifacts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('discoverer_id', sa.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'))
    )
    op.create_index(op.f('ix_recipes_artifact_id'), 'recipes', ['artifact_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_recipes_artifact_id'), table_name='recipes')
    op.drop_table('recipes')
    
    op.drop_index(op.f('ix_artifacts_player_id'), table_name='artifacts')
    op.drop_table('artifacts')
    
    op.drop_index(op.f('ix_expeditions_player_id'), table_name='expeditions')
    op.drop_table('expeditions')
    
    # expedition_status = sa.Enum('pending', 'active', 'completed', 'claimed', name='expeditionstatus')
    # expedition_status.drop(op.get_bind())
    pass
    
    op.drop_index(op.f('ix_ships_player_id'), table_name='ships')
    op.drop_table('ships')
    
    op.drop_table('players')