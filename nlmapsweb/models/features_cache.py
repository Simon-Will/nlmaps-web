import pickle

from sqlalchemy.exc import IntegrityError

from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


class FeaturesCacheEntry(BaseModel):
    __tablename__ = 'features_cache'

    mrl = db.Column(db.Unicode(500), unique=True, index=True, nullable=False)
    pickled_features = db.Column(db.CHAR(500), nullable=True)

    @classmethod
    def get_features_by_mrl(cls, mrl):
        entry = cls.query.filter_by(mrl=mrl).first()
        if entry and entry.pickled_features:
            return pickle.loads(entry.pickled_features)
        return None

    @classmethod
    def create(cls, mrl, features):
        pickled_features = pickle.dumps(features)
        if len(mrl) < 500 and len(pickled_features) < 500:
            entry = cls(mrl=mrl, pickled_features=pickled_features)
            db.session.add(entry)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
