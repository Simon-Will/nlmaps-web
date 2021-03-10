from functools import wraps

from flask import current_app, flash, redirect, request, url_for
from flask_login import current_user


def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        if not current_user.admin:
            flash('You are not allowed to access {}'.format(request.url),
                  'error')
            return redirect(url_for('profile'))
        return func(*args, **kwargs)

    return decorated_view
