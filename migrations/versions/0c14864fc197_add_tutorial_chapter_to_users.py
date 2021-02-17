"""Add tutorial_chapter to users

Revision ID: 0c14864fc197
Revises: 7f995044aa9f
Create Date: 2021-02-14 17:02:00.685770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c14864fc197'
down_revision = '7f995044aa9f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('tutorial_chapter', sa.Integer(),
                                      nullable=False, server_default='1'))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('tutorial_chapter')
