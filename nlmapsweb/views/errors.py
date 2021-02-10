import traceback

from flask import current_app, render_template, request
from flask_login import current_user

from nlmapsweb.mt_server import MTServerError


@current_app.errorhandler(403)
def page_forbidden(e):
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.warning('Error 403. URL {} requested by {}. {}'
                               .format(request.url, username, e))
    return render_template('403.html'), 403


@current_app.errorhandler(404)
def page_not_found(e):
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.warning('Error 404. URL {} requested by {}. {}'
                               .format(request.url, username, e))
    return render_template('404.html'), 404


@current_app.errorhandler(Exception)
def internal_server_error(e):
    trace = traceback.format_exc()
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.error(
        'Error 500. URL {} requested by {}. {}'
        .format(request.url, username, trace)
    )
    return render_template('500.html'), 500


@current_app.errorhandler(MTServerError)
def mt_server_error(e):
    trace = traceback.format_exc()
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.error(
        'MTServerError. URL {} requested by {}. {}'
        .format(request.url, username, trace)
    )
    return render_template('mt_server_error.html'), 500
