"""Add email to user and change password column

Revision ID: b0e65c0c4b55
Revises: 0c14864fc197
Create Date: 2021-02-28 22:02:57.589129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0e65c0c4b55'
down_revision = '0c14864fc197'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
            'users', table_args=(sa.UniqueConstraint('email'),)) as batch_op:
        batch_op.add_column(sa.Column('email', sa.Unicode(length=200),
                                      nullable=False, server_default=''))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email')
