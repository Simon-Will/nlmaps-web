from flask_login import current_user, login_required
from flask import (current_app, jsonify, redirect, render_template, request,
                   url_for)
import requests

from nlmapsweb.forms import ParsingModelForm
from nlmapsweb.utils.auth import admin_required


def _check_train_status():
    url = current_app.config['JOEY_SERVER_URL'] + 'train_status'
    response = requests.get(url)
    if not response.ok:
        return jsonify({'error': 'Error in parsing server'}), 500
    return response.json()


@current_app.route('/train', methods=['GET', 'POST'])
@admin_required
def train():
    error = None
    status = 200

    form = ParsingModelForm()
    if form.validate_on_submit():
        model = form.model.data
        url = current_app.config['JOEY_SERVER_URL'] + 'train'
        response = requests.post(url, json={'model': model})
        if response.ok:
            return redirect(url_for('train'))
        else:
            train_status = _check_train_status()
            if train_status.get('still_training'):
                error = 'Training already running.'
            else:
                error = 'Error in parsing server.'
            status = 500
    else:
        model = current_app.config['CURRENT_MODEL']
        form.model.process_data(model)

    return render_template('train.html', error=error, form=form, model=model), status


@current_app.route('/train_status', methods=['GET'])
@admin_required
def check_train_status():
    return jsonify(_check_train_status())
