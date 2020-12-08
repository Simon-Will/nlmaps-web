from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, Unicode

from nlmapsweb.models.base import BaseModel


class User(BaseModel, UserMixin):

    __tablename__ = 'users'

    name = Column(Unicode(100), nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    admin = Column(Boolean, nullable=False, default=False)
    password_hash = Column(Unicode(128), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False

    @property
    def is_active(self):
        return self.active
