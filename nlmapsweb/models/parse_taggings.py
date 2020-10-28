from sqlalchemy import Column, Integer, ForeignKey, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel


class ParseTagging(BaseModel):

    __tablename__ = 'parse_taggings'

    parse_log_id = Column(Integer, ForeignKey('parse_logs.id'))
    feedback_id = Column(Integer, ForeignKey('feedback.id'))
    tag_id = Column(Integer, ForeignKey('tags.id'))

    parse_log = relationship('ParseLog', back_populates='parse_taggings')
    feedback_piece = relationship('Feedback', back_populates='parse_taggings')
    tags = relationship('Tag', back_populates='parse_taggings')
