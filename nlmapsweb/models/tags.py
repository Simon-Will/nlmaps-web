from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


class Tag(BaseModel):

    __tablename__ = 'tags'

    name = db.Column(
        db.Unicode(100),
        nullable=False,
        unique=True,
    )

    parse_taggings = db.relationship('ParseTagging', back_populates='tags')
