"""Add column annotation_mode to users table

Revision ID: d6d1885839ce
Revises: 4d09e22bbb95
Create Date: 2021-03-25 20:05:48.083330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6d1885839ce'
down_revision = '4d09e22bbb95'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('annotation_mode', sa.Boolean(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('users', 'annotation_mode')
