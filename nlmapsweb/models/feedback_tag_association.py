from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


feedback_tag_association = db.Table(
    'feedback_tag_association',
    BaseModel.metadata,
    db.Column('feedback_id', db.Integer, db.ForeignKey('feedback.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
)
