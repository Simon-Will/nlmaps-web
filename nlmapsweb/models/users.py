from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


class User(BaseModel, UserMixin):

    __tablename__ = 'users'

    name = db.Column(db.Unicode(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.Unicode(128), nullable=True)

    #feedback_states = db.relationship('FeedbackState', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return ('User(id={u.id}, name={u.name}, active={u.active},'
                ' admin={u.admin})').format(u=self)
