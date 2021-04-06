"""Add name_occurrences table

Revision ID: e778713634b0
Revises: 9e0a0d9fc125
Create Date: 2021-04-05 18:20:48.673349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e778713634b0'
down_revision = '9e0a0d9fc125'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('name_occurrences',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('name', sa.Unicode(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uniq_idx_name_user', 'name_occurrences', ['name', 'user_id'], unique=True)


def downgrade():
    op.drop_index('uniq_idx_name_user', table_name='name_occurrences')
    op.drop_table('name_occurrences')
