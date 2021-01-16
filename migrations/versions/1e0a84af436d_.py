"""empty message

Revision ID: 1e0a84af436d
Revises: 1989208b19e3
Create Date: 2020-10-24 22:53:25.408545

"""
from collections import defaultdict
import datetime

from alembic import op
import sqlalchemy as sa

from nlmaps_tools.mrl import NLmaps

# revision identifiers, used by Alembic.
revision = '1e0a84af436d'
down_revision = '1989208b19e3'
branch_labels = None
depends_on = None


def upgrade():
    metadata = sa.MetaData()
    feedback = sa.Table(
        'feedback',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True,
                  nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('nl', sa.Unicode(500), nullable=False),
        sa.Column('systemMrl', sa.Unicode(500), nullable=True),
        sa.Column('correctMrl', sa.Unicode(500), nullable=True),
    )
    tags = sa.Table(
        'tags',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True,
                  nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('name', sa.Unicode(100), nullable=False, unique=True),
    )
    feedback_tag_association = sa.Table(
        'feedback_tag_association',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True,
                  nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('feedback_id', sa.Integer, sa.ForeignKey('feedback.id')),
        sa.Column('tag_id', sa.Integer),
    )
    parse_logs = sa.Table(
        'parse_logs',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True,
                  nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('nl', sa.Unicode(500), nullable=False),
        sa.Column('lin', sa.Unicode(500), nullable=True),
    )

    conn = op.get_bind()

    now = datetime.datetime.now(datetime.timezone.utc)
    conn.execute(tags.insert().values({'name': 'correct', 'created': now}))
    correct_tag_id = conn.execute(
        sa.select([tags.c.id]).where(tags.c.name == 'correct')
    ).fetchall()[0][0]
    correct_feedback_pieces = conn.execute(
        sa.select([feedback.c.id])
        .where(feedback.c.systemMrl == feedback.c.correctMrl)
    ).fetchall()
    tagged_feedback_ids = {
        tup[0] for tup in conn.execute(
            sa.select([feedback_tag_association.c.feedback_id])
        )
    }
    correct_feedback_tag_entries = [
        {'tag_id': correct_tag_id, 'feedback_id': tup[0]}
        for tup in correct_feedback_pieces
        if tup[0] not in tagged_feedback_ids
    ]
    conn.execute(feedback_tag_association.insert().values(),
                 correct_feedback_tag_entries)

    for tup in correct_feedback_pieces:
        feedback_id = tup[0]
        feedback_tag_association.insert()

    result = conn.execute(sa.select([
        feedback.c.id, feedback.c.nl, feedback.c.systemMrl,
        feedback_tag_association.c.tag_id
    ]).select_from(feedback.join(feedback_tag_association))).fetchall()

    feedback_tag_parse_log = []
    for feedback_id, nl, system_mrl, tag_id in result:
        parse_log_ids = conn.execute(sa.select([parse_logs.c.id, parse_logs.c.lin])
                                     .where(parse_logs.c.nl == nl)).fetchall()
        for pl_id, pl_lin in parse_log_ids:
            if pl_lin:
                feedback_tag_parse_log.append((feedback_id, tag_id, pl_id))
                break
        else:
            if system_mrl:
                lin = NLmaps().preprocess_mrl(system_mrl.strip())
            else:
                lin = None
            now = datetime.datetime.now(datetime.timezone.utc)
            insert_result = conn.execute(
                parse_logs.insert()
                .values({'nl': nl, 'lin': lin, 'created': now})
            )
            [pl_id] = insert_result.inserted_primary_key
            feedback_tag_parse_log.append((feedback_id, tag_id, pl_id))

    op.drop_table('feedback_tag_association')

    op.create_table('parse_taggings',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('parse_log_id', sa.Integer(), nullable=True),
                    sa.Column('feedback_piece_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['feedback_piece_id'], ['feedback.id'], ),
                    sa.ForeignKeyConstraint(['parse_log_id'], ['parse_logs.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


    with op.batch_alter_table("parse_logs") as batch_op:
        batch_op.add_column(sa.Column('model', sa.Unicode(length=200), nullable=True))
        batch_op.add_column(sa.Column('mrl', sa.Unicode(length=500), nullable=True))
        op.execute("UPDATE parse_logs SET model = 'staniek_nlmaps_lin_char'")
        batch_op.alter_column('model', nullable=False)

    parse_logs = sa.Table(
        'parse_logs',
        metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True,
                  nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('nl', sa.Unicode(500), nullable=False),
        sa.Column('model', sa.Unicode(200), nullable=False),
        sa.Column('lin', sa.Unicode(500), nullable=True),
        sa.Column('mrl', sa.Unicode(500), nullable=True),
    )

    parse_logs_to_keep = {pl_id for _, _, pl_id in feedback_tag_parse_log}
    for tup in conn.execute(sa.select([parse_logs.c.id])).fetchall():
        pl_id = tup[0]
        if pl_id not in parse_logs_to_keep:
            conn.execute(parse_logs.delete().where(parse_logs.c.id == pl_id))


    for tag_id, feedback_id, pl_id in feedback_tag_parse_log:
        [lin] = conn.execute(sa.select([parse_logs.c.lin])
                             .where(parse_logs.c.id == pl_id)).fetchone()
        try:
            mrl = NLmaps().functionalise(lin.strip())
        except:
            mrl = None
        conn.execute(parse_logs.update()
                     .where(parse_logs.c.id == pl_id)
                     .values(mrl=mrl))

    now = datetime.datetime.now(datetime.timezone.utc)
    op.bulk_insert('parse_taggings', [
        {'parse_log_id': pl_id, 'feedback_piece_id': feedback_id,
         'tag_id': tag_id, 'created': now}
        for tag_id, feedback_id, pl_id in feedback_tag_parse_log
    ])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parse_logs', 'mrl')
    op.drop_column('parse_logs', 'model')
    op.create_table('feedback_tag_association',
                    sa.Column('feedback_id', sa.INTEGER(), nullable=True),
                    sa.Column('tag_id', sa.INTEGER(), nullable=True),
                    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
                    )
    op.drop_table('parse_taggings')
    # ### end Alembic commands ###
