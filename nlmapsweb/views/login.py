from flask_login import current_user, login_required, login_user, logout_user
from flask import (current_app, flash, redirect, render_template, request,
                   url_for)

from nlmapsweb.app import db
from nlmapsweb.forms import LoginForm, RegisterForm
from nlmapsweb.models import User


@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('query'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password_hash(form.password.data):
            flash('Login failed.', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('query'))

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
        login_user(user, remember=True)
        return redirect(url_for('query'))

    for error in form.formatted_errors:
        flash(error, 'error')

    form.password.process_data('')
    form.password2.process_data('')
    return render_template('register.html', form=form)
