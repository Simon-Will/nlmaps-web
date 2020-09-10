from sqlalchemy import Column, Unicode

from nlmapsweb.models.base import BaseModel


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
        # TODO: Resolve this import hell …
        from nlmapsweb.processing.converting import functionalise
        return functionalise(self.lin)
