from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel


class Tag(BaseModel):

    __tablename__ = 'tags'

    name = Column(
        Unicode(100),
        nullable=False,
        unique=True,
    )

    parse_taggings = relationship('ParseTagging', back_populates='tags')
