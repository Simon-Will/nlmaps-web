import datetime as dt

from flask_login import current_user
from flask import current_app, render_template, request

import nlmapsweb.mt_server as mt_server
from nlmapsweb.utils.auth import admin_required
from nlmapsweb.utils.plotting import fig_to_base64, plot_validations


@current_app.route('/validations', methods=['GET'])
@admin_required
def validations():
    label = request.args.get('label')
    if label:
        params = {'label': label}
    else:
        params = None
    response = mt_server.get('/validations', params=params)

    eval_results = response.json()
    for val in eval_results:
        val['created'] = dt.datetime.fromisoformat(val['created'])

    figure = plot_validations(eval_results)
    base64_jpg = fig_to_base64(figure, 'jpg')

    return render_template('validations.html', validations=eval_results,
                           base64_jpg=base64_jpg)
