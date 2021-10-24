import traceback

from flask import current_app, jsonify, render_template, request
from flask_login import current_user

from nlmaps_web.mt_server import MTServerError


def error_response(html_template, message):
    if (not request.accept_mimetypes.accept_html
        and request.accept_mimetypes.accept_json):
        return jsonify({'error': message})
    else:
        return render_template(html_template)


@current_app.errorhandler(403)
def page_forbidden(e):
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.warning('Error 403. URL {} requested by {}. {}'
                               .format(request.url, username, e))
    return error_response('403.html', 'Forbidden'), 403


@current_app.errorhandler(404)
def page_not_found(e):
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.warning('Error 404. URL {} requested by {}. {}'
                               .format(request.url, username, e))
    return error_response('404.html', 'Not Found'), 404


@current_app.errorhandler(Exception)
def internal_server_error(e):
    trace = traceback.format_exc()
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.error(
        'Error 500. URL {} requested by {}. {}'
        .format(request.url, username, trace)
    )
    return error_response('500.html', 'Internal Server Error'), 500


@current_app.errorhandler(MTServerError)
def mt_server_error(e):
    trace = traceback.format_exc()
    username = (current_user.name if current_user.is_authenticated
                else '[Anonmyous]')
    current_app.logger.error(
        'MTServerError. URL {} requested by {}. {}'
        .format(request.url, username, trace)
    )
    return error_response('mt_server_error.html',
                          'Machine Translation Server Unreachable'), 500
