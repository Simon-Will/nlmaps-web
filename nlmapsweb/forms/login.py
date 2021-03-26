from flask_login import current_user
from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from nlmapsweb.forms.base import BaseForm
from nlmapsweb.models import Token, User
from nlmapsweb.utils.helper import get_utc_now


class PasswordSetMixin:
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

    def validate_password(self, field):
        password = field.data
        password2 = self.password2.data
        if not password == password2:
            raise ValidationError('The given passwords do not match.')


class EmailSetMixin:
    email = EmailField(
        'Email Address',
        validators=[DataRequired()]
    )

    def validate_email(self, field):
        wanted_email = field.data
        if User.query.filter_by(name=wanted_email).first():
            raise ValidationError('Email {} is already taken.'
                                  .format(wanted_email))


class LoginForm(BaseForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(BaseForm, PasswordSetMixin, EmailSetMixin):
    name = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=99)],
        render_kw={
            'pattern': r'[abcdefghijklmnopqrstuvwxyz0123456789_.-]{2,99}',
            'title': ('Length should be 2-99. Allowed characters:'
                      ' abcdefghijklmnopqrstuvwxyz0123456789_.-'),
        },
    )

    accepted_terms = BooleanField('Terms of Service')

    def validate_name(self, field):
        wanted_name = field.data

        allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789_.-'
        if any(c not in allowed_chars for c in wanted_name):
            raise ValidationError(
                'Only the lower case characters {} are allowed in the name.'
                .format(allowed_chars)
            )

        if User.query.filter_by(name=wanted_name).first():
            raise ValidationError('Name {} is already taken.'
                                  .format(wanted_name))

    def validate_accepted_terms(self, field):
        if field.data is not True:
            raise ValidationError('You must accept the terms of service.')


class ProfileForm(BaseForm, EmailSetMixin):
    contributor_name = StringField(
        'Contributor Name',
        validators=[Optional(), Length(min=2, max=200)],
    )
    annotation_mode = BooleanField('Annotation Controls')


class ChangePasswordForm(BaseForm, PasswordSetMixin):
    old_password = PasswordField(
        'Old Password',
        validators=[DataRequired()]
    )

    def validate_old_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Old password is incorrect.')


class ResetPasswordForm(BaseForm):
    email = EmailField(
        'Email Address',
        validators=[DataRequired()]
    )


class SetNewPasswordForm(BaseForm, PasswordSetMixin):
    code = HiddenField(
        'Code',
        validators=[DataRequired(), Length(min=36, max=36)],
    )

    def validate_token(self, field):
        token = Token.query.filter_by(code=field.data).first()
        if not token:
            raise ValidationError('The token {} is invalid.')
        now = get_utc_now()
        if now > token.expires:
            raise ValidationError(
                'The token {} is expired, but you can request a new one.')


class DeleteAccountForm(BaseForm):
    password = PasswordField('Password', validators=[DataRequired()])

    def validate_password(self, field):
        if not current_user.check_password(field.data):
            return ValidationError('Password incorrect.')
