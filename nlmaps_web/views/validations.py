import datetime as dt

from flask_login import current_user
from flask import current_app, render_template, request

import nlmaps_web.mt_server as mt_server
from nlmaps_web.forms.validations import ValidationsForm
from nlmaps_web.utils.auth import admin_required
from nlmaps_web.utils.plotting import fig_to_base64, plot_validations


@current_app.route('/validations', methods=['GET'])
@admin_required
def validations():
    form = ValidationsForm(request.args)
    if form.model.data:
        model = form.model.data
    else:
        model = current_app.config['CURRENT_MODEL']
        form.model.process_data(model)

    params = {'model': model}
    if form.label.data:
        params['label'] = form.label.data

    response = mt_server.get('/validations', params=params)

    eval_results = response.json()
    for val in eval_results:
        val['created'] = dt.datetime.fromisoformat(val['created'])

    figure = plot_validations(eval_results)
    base64_jpg = fig_to_base64(figure, 'jpg')

    return render_template('validations.html', form=form,
                           validations=eval_results, base64_jpg=base64_jpg)
