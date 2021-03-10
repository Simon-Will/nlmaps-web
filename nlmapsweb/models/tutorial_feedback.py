from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


class TutorialFeedback(BaseModel):
    __tablename__ = 'tutorial_feedback'
    content = db.Column(db.Unicode(2000), nullable=False)
