from flask_login import current_user, login_required
from flask import (current_app, jsonify, redirect, render_template, request,
                   url_for)

from nlmapsweb.forms import ParsingModelForm
import nlmapsweb.mt_server as mt_server
from nlmapsweb.utils.auth import admin_required


def _check_train_status():
    response = mt_server.get('train_status')
    if not response.ok:
        return jsonify({'error': 'Error in parsing server'}), 500
    return response.json()


@current_app.route('/train', methods=['GET', 'POST'])
@admin_required
def train():
    """Serve training monitoring page with option of starting training."""
    error = None
    status = 200

    form = ParsingModelForm()
    if form.validate_on_submit():
        model = form.model.data
        response = mt_server.post('train', json={'model': model})
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
    """Check if training is running on the machine translation server.

    Use by Ajax.
    """
    return jsonify(_check_train_status())
