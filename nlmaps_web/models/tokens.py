from nlmaps_web.app import db
from nlmaps_web.models.base import BaseModel


class Token(BaseModel):
    __tablename__ = 'tokens'

    code = db.Column(db.CHAR(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    expires = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )
