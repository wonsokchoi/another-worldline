"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-27 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('nickname', sa.String(length=50), nullable=True),
        sa.Column('daily_free_pulls_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_pull_reset_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('coupon_balance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('race', sa.String(length=50), nullable=False, server_default='인간'),
        sa.Column('hp', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('mp', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('strength', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('intelligence', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('agility', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('luck', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('charm', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('equipment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pets', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('relationships', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rarity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('worldline_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_characters_user_id'), 'characters', ['user_id'], unique=False)

    # Create worldlines table
    op.create_table(
        'worldlines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('worldline_number', sa.Integer(), nullable=False),
        sa.Column('genre', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('story_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_worldlines_character_id'), 'worldlines', ['character_id'], unique=False)

    # Create stories table
    op.create_table(
        'stories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('worldline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('genre', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('stat_changes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('items_gained', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sequence_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
        sa.ForeignKeyConstraint(['worldline_id'], ['worldlines.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stories_character_id'), 'stories', ['character_id'], unique=False)
    op.create_index(op.f('ix_stories_worldline_id'), 'stories', ['worldline_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_stories_worldline_id'), table_name='stories')
    op.drop_index(op.f('ix_stories_character_id'), table_name='stories')
    op.drop_table('stories')
    op.drop_index(op.f('ix_worldlines_character_id'), table_name='worldlines')
    op.drop_table('worldlines')
    op.drop_index(op.f('ix_characters_user_id'), table_name='characters')
    op.drop_table('characters')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_table('users')
