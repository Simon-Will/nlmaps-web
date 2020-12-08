from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm


class LoginForm(BaseForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
