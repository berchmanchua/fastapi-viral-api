"""initial items table

Revision ID: 001_initial_items
Revises: 
Create Date: 2026-11-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: Union[str, None] = '001_initial_items'
down_revision: Union[str, None] = None
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('viral_score', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create optimized partial index concurrently for active rows
    with op.get_context().autocommit_block():
        op.create_index(
            'idx_items_active_viral_score',
            'items',
            [sa.text('viral_score DESC')],
            postgresql_where=sa.text('deleted_at IS NULL'),
            postgresql_concurrently=True
        )


def downgrade() -> None:
    op.drop_index('idx_items_active_viral_score', table_name='items', postgresql_concurrently=True)
    op.drop_table('items')
