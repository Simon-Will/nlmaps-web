from nlmaps_web.app import db
from nlmaps_web.models.base import BaseModel


class FeedbackState(BaseModel):

    __tablename__ = 'feedback_states'

    feedback_id = db.Column(db.Integer, nullable=False)
    model = db.Column(db.Unicode(500), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
