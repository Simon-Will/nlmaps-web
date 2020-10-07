from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel
from nlmapsweb.models.feedback_tag_association import feedback_tag_association


class Tag(BaseModel):

    __tablename__ = 'tags'

    name = Column(
        Unicode(100),
        nullable=False,
        unique=True,
    )

    feedback_pieces = relationship(
        'Feedback',
        secondary=feedback_tag_association,
        back_populates='tags'
    )
