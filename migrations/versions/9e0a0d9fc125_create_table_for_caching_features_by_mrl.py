"""Create table for caching features by mrl

Revision ID: 9e0a0d9fc125
Revises: d6d1885839ce
Create Date: 2021-03-26 16:28:33.409423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e0a0d9fc125'
down_revision = 'd6d1885839ce'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('features_cache',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('mrl', sa.Unicode(length=500), nullable=False),
    sa.Column('pickled_features', sa.CHAR(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_features_cache_mrl'), 'features_cache', ['mrl'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_features_cache_mrl'), table_name='features_cache')
    op.drop_table('features_cache')
