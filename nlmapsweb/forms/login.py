from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, ValidationError

from nlmapsweb.forms.base import BaseForm
from nlmapsweb.models import User


class LoginForm(BaseForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(BaseForm):
    name = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=99)],
        render_kw={
            'pattern': r'[abcdefghijklmnopqrstuvwxyz_.-]{2,99}',
            'title': ('Length should be 2-99. Allowed characters:'
                      ' abcdefghijklmnopqrstuvwxyz_.-'),
        },
    )

    email = EmailField(
        'Email Address',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)],
        render_kw={'minlength': '8'},
    )

    password2 = PasswordField(
        'Repeat password',
        validators=[DataRequired()],
        render_kw={'minlength': '8'},
    )

    def validate_name(self, field):
        wanted_name = field.data

        allowed_chars = 'abcdefghijklmnopqrstuvwxyz_.-'
        if any(c not in allowed_chars for c in wanted_name):
            raise ValidationError(
                'Only the lower case characters {} are allowed in the name.'
                .format(allowed_chars)
            )

        if User.query.filter_by(name=wanted_name).first():
            raise ValidationError('Name {} is already taken.'
                                  .format(wanted_name))

    def validate_email(self, field):
        wanted_email = field.data
        if User.query.filter_by(name=wanted_email).first():
            raise ValidationError('Email {} is already taken.'
                                  .format(wanted_email))

    def validate_password(self, field):
        password = field.data
        password2 = self.password2.data
        if not password == password2:
            raise ValidationError('The given passwords do not match.')


class ChangePasswordForm(BaseForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired()])

    def validate_password(self, field):
        password = field.data
        password2 = self.password2.data
        if not password == password2:
            raise ValidationError('The given passwords do not match.')
