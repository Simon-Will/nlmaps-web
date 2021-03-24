from flask_login import current_user
from flask import current_app, render_template, request

import nlmapsweb.mt_server as mt_server
from nlmapsweb.utils.auth import admin_required


@current_app.route('/validations', methods=['GET'])
@admin_required
def validations():
    label = request.args.get('label')
    if label:
        params = {'label': label}
    else:
        params = None
    response = mt_server.get('/validations', params=params)
    evaluation_results = response.json()

    return render_template('validations.html',
                           evaluation_results=evaluation_results)
