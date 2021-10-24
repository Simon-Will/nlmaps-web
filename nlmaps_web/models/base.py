from sqlalchemy import Column, DateTime, Integer

from nlmaps_web.app import db
from nlmaps_web.utils.helper import get_utc_now


class BaseModel(db.Model):

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False
    )

    created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=get_utc_now
    )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        sorted_attributes = sorted(
            (col.name, getattr(self, col.name))
            for col in self.__table__.columns
        )
        attributes = ', '.join(f'{a[0]}={a[1]!r}' for a in sorted_attributes)
        return f'{class_name}({attributes})'
