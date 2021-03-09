import datetime as dt

from flask_login import current_user, login_required, login_user, logout_user
from flask import (current_app, flash, redirect, render_template, request,
                   url_for)

from nlmapsweb.app import db
from nlmapsweb.utils.emailing import send_mail
from nlmapsweb.utils.helper import get_utc_now, random_string_with_digits
from nlmapsweb.forms import (ChangePasswordForm, DeleteAccountForm, LoginForm,
                             ProfileForm, RegisterForm, ResetPasswordForm,
                             SetNewPasswordForm)
from nlmapsweb.models import Token, User


def send_welcome_mail(user):
    nlmaps_url = request.url_root
    message = (
        'Hello {name},\r\n'
        '\r\n'
        'thanks for registering for NLMaps Web at {url}!'
        'We hope you will enjoy our service.\r\n'
        '\r\n'
        'If it wasn’t you who registered with this email address, you can go'
        ' to our site, log in, reset your password and delete the account.\r\n'
        '\r\n'
        'Have a nice day!\r\n'
        .format(name=user.name, url=nlmaps_url)
    )
    subject = 'Welcome to NLMaps Web'
    send_mail(message=message, subject=subject, to=user.email)


def send_password_reset_mail(user, token):
    url = url_for('set_new_password', code=token.code, _external=True)
    message = (
        'Hello {name},\r\n'
        '\r\n'
        'You can reset your password here:\r\n'
        '\r\n'
        '{url}\r\n'
        .format(name=user.name, url=url)
    )
    subject = 'Welcome to NLMaps Web'
    send_mail(message=message, subject=subject, to=user.email)


@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('query'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Login failed.', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('profile'))

    return render_template('login.html', form=form)


@current_app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('query'))


@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('query'))

    form = RegisterForm()
    if form.validate_on_submit():
        data = form.get_data()
        user = User(name=data['name'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        send_welcome_mail(user)
        login_user(user, remember=True)
        return redirect(url_for('profile'))

    for error in form.formatted_errors:
        flash(error, 'error')

    form.password.data = ''
    form.password2.data = ''
    return render_template('register.html', form=form)


@current_app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')


@current_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.contributor_name = form.contributor_name.data
        db.session.add(current_user)
        db.session.commit()
        flash('Profile changed.')
        return redirect(url_for('profile'))

    for error in form.formatted_errors:
        flash(error, 'error')

    return render_template('edit_profile.html', form=form)


@current_app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.add(current_user)
        db.session.commit()
        flash('Password changed.')
        return redirect(url_for('profile'))

    for error in form.formatted_errors:
        flash(error, 'error')

    form.password.data = ''
    form.password2.data = ''
    return render_template('change_password.html', form=form)


@current_app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('change_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            expiry_time = get_utc_now() + dt.timedelta(hours=24)
            token = Token(code=random_string_with_digits(36),
                          user_id=user.id, expires=expiry_time)
            db.session.add(token)
            db.session.commit()
            send_password_reset_mail(user, token)
        flash('If the email {} is associated with an account, a password reset'
              ' link has been sent.'.format(email))
        return redirect(url_for('login'))

    for error in form.formatted_errors:
        flash(error, 'error')

    return render_template('reset_password.html', form=form)


@current_app.route('/set_new_password/<code>', methods=['GET', 'POST'])
def set_new_password(code):
    form = SetNewPasswordForm(data={'code': code})
    if form.validate_on_submit():
        token = Token.query.filter_by(code=form.code.data).first()
        user = User.query.get(token.user_id)
        user.set_password(form.password.data)

        db.session.delete(token)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash('Password changed.')
        return redirect(url_for('profile'))

    for error in form.formatted_errors:
        flash(error, 'error')

    return render_template('set_new_password.html', form=form)


@current_app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        current_user.name = random_string_with_digits(10)
        current_user.email = random_string_with_digits(10)
        current_user.active = False
        current_user.set_password(random_string_with_digits(10))

        db.session.add(current_user)
        db.session.commit()
        logout_user()
        flash('Account deleted.')
        return redirect(url_for('query'))

    for error in form.formatted_errors:
        flash(error, 'error')

    return render_template('delete_account.html', form=form)
