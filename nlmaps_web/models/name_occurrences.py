from sqlalchemy import Index

from nlmaps_web.app import db
from nlmaps_web.models.base import BaseModel


class NameOccurrence(BaseModel):
    __tablename__ = 'name_occurrences'

    __table_args__ = (
        Index('uniq_idx_name_user', 'name', 'user_id', unique=True),
    )

    name = db.Column(db.Unicode(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    count = db.Column(db.Integer, default=0)

    @classmethod
    def get_count(cls, name, user_id):
        occ = cls.query.filter_by(name=name, user_id=user_id).first()
        if occ:
            return occ.count
        return 0

    @classmethod
    def increment(cls, name, user_id, incr=1):
        occ = cls.query.filter_by(name=name, user_id=user_id).first()
        if occ:
            occ.count += incr
        else:
            occ = cls(name=name, user_id=user_id, count=incr)
        db.session.add(occ)
        db.session.commit()
        return occ.count
