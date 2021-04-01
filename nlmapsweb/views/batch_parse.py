from flask import current_app, jsonify

from nlmapsweb.forms.parsing_model import ParsingModelForm
import nlmapsweb.mt_server as mt_server
from nlmapsweb.processing.parsing import parse_to_lin


@current_app.route('/batch_parse', methods=['POST'])
def batch_parse():
    form = ParsingModelForm()
    if form.validate_on_submit():
        model = form.model.data
        filters = {'model': model}

        response = mt_server.post('query_feedback', json=filters)
        nls = []
        for feedback_info in response.json()['feedback']:
            if not feedback_info['model_lin']:
                nls.append(feedback_info['nl'])
        result = parse_to_lin(nls, model=model)
        return jsonify(result)

    return 'Bad Request', 400
