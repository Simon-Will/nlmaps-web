from multiprocessing.pool import ThreadPool

from flask import current_app, jsonify
import requests

from nlmapsweb.forms.parsing_model import ParsingModelForm
from nlmapsweb.processing.parsing import parse_to_lin


@current_app.route('/batch_parse', methods=['POST'])
def batch_parse():
    form = ParsingModelForm()
    if form.validate_on_submit():
        model = form.model.data
        filters = {'model': model}

        url = current_app.config['JOEY_SERVER_URL'] + 'query_feedback'

        response = requests.post(url, json=filters)
        nls = []
        for feedback_info in response.json():
            if not feedback_info['model_lin']:
                nls.append(feedback_info['nl'])
        result = parse_to_lin(nls, model=model)
        return jsonify(result)

    return 'Bad Request', 400
