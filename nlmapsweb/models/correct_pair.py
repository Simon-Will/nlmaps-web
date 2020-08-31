from sqlalchemy import Column, Unicode

from nlmapsweb.models.base import BaseModel


class CorrectPair(BaseModel):

    __tablename__ = 'correct_pairs'

    nl = Column(
        Unicode(500),
        nullable=False,
    )

    mrl = Column(
        Unicode(500),
        nullable=False,
    )
