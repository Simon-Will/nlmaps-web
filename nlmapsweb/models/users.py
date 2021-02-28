import bcrypt
from flask_login import UserMixin

from nlmapsweb.app import db
from nlmapsweb.models.base import BaseModel


def hash_password(password, rounds=14):
    password_hash = bcrypt.hashpw(password.encode('utf-8'),
                                  bcrypt.gensalt(rounds))
    return password_hash


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash)


class User(BaseModel, UserMixin):
    __tablename__ = 'users'

    name = db.Column(db.Unicode(100), nullable=False, unique=True)
    email = db.Column(db.Unicode(200), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.CHAR(60), nullable=True)

    # Should be set to -1 when the tutorial is completed.
    tutorial_chapter = db.Column(db.Integer, nullable=False, default=1,
                                 server_default='1')

    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password_hash(self, password):
        if self.password_hash:
            return check_password(password, self.password_hash)
        return False

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return ('User(id={u.id}, name={u.name}, active={u.active},'
                ' admin={u.admin})').format(u=self)
