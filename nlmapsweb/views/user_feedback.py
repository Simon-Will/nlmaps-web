from flask import current_app, jsonify, render_template, request
from flask_login import current_user
import requests

from nlmapsweb.models import FeedbackState, ParsingModelForm
from nlmapsweb.processing.converting import functionalise


class Feedback:

    def __init__(self, id, nl, correct_lin, original_model,
                 original_lin, parent_id=None, model=None,
                 model_lin=None, correct_mrl=None, original_mrl=None,
                 model_mrl=None):
        self.id = id
        self.nl = nl
        self.correct_lin = correct_lin
        self.original_model = original_model
        self.original_lin = original_lin
        self.parent_id = parent_id

        self.model = model
        self.model_lin = model_lin

        self.correct_mrl = correct_mrl or functionalise(correct_lin)
        self.original_mrl = original_mrl or functionalise(original_lin)
        self.model_mrl = model_mrl or functionalise(model_lin)

    @classmethod
    def get_multiple_from_server(cls, model=None, user_id=None, url=None):
        if not url:
            url = current_app.config['JOEY_SERVER_URL']
            url += 'query_feedback'

        filters = {}
        if model:
            filters['model'] = model
        if user_id:
            filters['user_id'] = user_id

        feedback_dicts = requests.post(url, json=filters)
        feedback = [cls(**piece) for piece in feedback_dicts]
        return feedback


@current_app.route('/my_queries', methods=['GET'])
def show_user_queries():
    if not current_user.is_authenticated:
        return 'Forbidden', 403

    parsing_model_form = ParsingModelForm(request.args)
    kwargs = {
        'model': parsing_model_form.data['model'],
        'user_id': current_user.id
    }
    feedback = Feedback.get_multiple_from_server(**kwargs)

    old_feedback_states = FeedbackState.query.filter_by(
        user_id=current_user.id).all()
