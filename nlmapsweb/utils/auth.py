from functools import wraps

from flask import current_app
from flask_login import current_user


def admin_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        if not (current_user.is_authenticated and current_user.admin):
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view
