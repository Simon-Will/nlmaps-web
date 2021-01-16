"""Create users, feedback_states, parse_logs

Revision ID: 7f995044aa9f
Revises: 
Create Date: 2021-01-16 12:49:23.239879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f995044aa9f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedback_states',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.Column('model', sa.Unicode(length=500), nullable=False),
    sa.Column('correct', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parse_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('nl', sa.Unicode(length=500), nullable=False),
    sa.Column('model', sa.Unicode(length=200), nullable=False),
    sa.Column('lin', sa.Unicode(length=500), nullable=True),
    sa.Column('mrl', sa.Unicode(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('parse_logs')
    op.drop_table('feedback_states')
    # ### end Alembic commands ###
