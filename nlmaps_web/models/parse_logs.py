from nlmaps_web.app import db
from nlmaps_web.models.base import BaseModel


class ParseLog(BaseModel):

    __tablename__ = 'parse_logs'

    nl = db.Column(
        db.Unicode(500),
        nullable=False,
    )

    model = db.Column(
        db.Unicode(200),
        nullable=False
    )

    lin = db.Column(
        db.Unicode(500),
        nullable=True,
    )

    mrl = db.Column(
        db.Unicode(500),
        nullable=True,
    )
