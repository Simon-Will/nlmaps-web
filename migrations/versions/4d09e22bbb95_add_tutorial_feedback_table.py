"""Add tutorial feedback table

Revision ID: 4d09e22bbb95
Revises: e70b623905d1
Create Date: 2021-03-10 13:43:56.115294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d09e22bbb95'
down_revision = 'e70b623905d1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tutorial_feedback',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('content', sa.Unicode(length=2000), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('tutorial_feedback')
