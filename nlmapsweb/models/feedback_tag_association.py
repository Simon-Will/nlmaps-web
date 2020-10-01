from sqlalchemy import Column, ForeignKey, Integer, Table

from nlmapsweb.models.base import BaseModel


feedback_tag_association = Table(
    'feedback_tag_association',
    BaseModel.metadata,
    Column('feedback_id', Integer, ForeignKey('feedback.id')),
    Column('tag_id', Integer, ForeignKey('tags.id')),
)
