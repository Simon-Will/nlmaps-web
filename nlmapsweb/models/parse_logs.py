from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel


class ParseLog(BaseModel):

    __tablename__ = 'parse_logs'

    nl = Column(
        Unicode(500),
        nullable=False,
    )

    model = Column(
        Unicode(200),
        nullable=False
    )

    lin = Column(
        Unicode(500),
        nullable=True,
    )

    mrl = Column(
        Unicode(500),
        nullable=True,
    )

    parse_taggings = relationship('ParseTagging', back_populates='parse_log')
