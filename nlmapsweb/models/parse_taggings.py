from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


class ParseTagging(BaseModel):

    __tablename__ = 'parse_taggings'

    parse_log_id = db.Column(db.Integer, db.ForeignKey('parse_logs.id'))
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))

    parse_log = db.relationship('ParseLog', back_populates='parse_taggings')
    feedback_piece = db.relationship('Feedback', back_populates='parse_taggings')
    tags = db.relationship('Tag', back_populates='parse_taggings')
