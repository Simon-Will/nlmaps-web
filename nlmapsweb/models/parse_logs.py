from sqlalchemy import Column, Unicode

from nlmapsweb.models.base import BaseModel
from nlmapsweb.parser import functionalise


class ParseLog(BaseModel):

    __tablename__ = 'parse_logs'

    nl = Column(
        Unicode(500),
        nullable=False,
    )

    lin = Column(
        Unicode(500),
        nullable=True,
    )

    @property
    def mrl(self):
        return functionalise(self.lin)
