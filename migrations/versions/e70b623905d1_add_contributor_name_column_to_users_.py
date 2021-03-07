"""Add contributor_name column to users table

Revision ID: e70b623905d1
Revises: e8ece01fdef2
Create Date: 2021-03-08 12:03:24.108119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e70b623905d1'
down_revision = 'e8ece01fdef2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('contributor_name', sa.Unicode(length=200),
                      server_default='', nullable=False)
        )


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('contributor_name')
