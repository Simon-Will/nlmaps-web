"""Add users table

Revision ID: 24d13b5fabeb
Revises: 1e0a84af436d
Create Date: 2020-12-07 11:39:55.398984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24d13b5fabeb'
down_revision = '1e0a84af436d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('name', sa.Unicode(length=100), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('password_hash', sa.Unicode(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('users')
