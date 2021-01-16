from flask_login import current_user, login_required
from flask import (abort, current_app, jsonify, redirect, render_template,
                   request, url_for)
import requests

from nlmapsweb.app import db
from nlmapsweb.forms import (AdminParsingModelForm, FeedbackCreateForm,
                             FeedbackEditForm, ParsingModelForm)
from nlmapsweb.models import FeedbackState
from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes
from nlmapsweb.processing.converting import delete_spaces, functionalise, linearise


def get_lin_and_mrl(lin, mrl):
    if lin and not mrl:
        mrl = functionalise(lin)
    elif mrl and not lin:
        lin = functionalise(mrl)
    return lin, mrl


class FeedbackPiece:

    def __init__(self, nl, id=None, parent_id=None, user_id=None, model=None,
                 correct_lin=None, correct_mrl=None, original_model=None,
                 original_lin=None, original_mrl=None, model_lin=None,
                 model_mrl=None, children=None):
        self.nl = nl
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.model = model
        self.original_model = original_model

        self.correct_lin, self.correct_mrl = get_lin_and_mrl(
            correct_lin, correct_mrl)
        if not self.correct_mrl:
            raise ValueError(
                'FeedbackPiece must have a correct_mrl, but it is None')

        self.original_lin, self.original_mrl = get_lin_and_mrl(
            original_lin, original_mrl)
        self.model_lin, self.model_mrl = get_lin_and_mrl(
            model_lin, model_mrl)

        self.children = children or []

    def get_opcodes(self, model=True, as_json=True):
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_opcodes(system_mrl, self.correct_mrl, as_json=as_json)

    def get_type(self, model=True):
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_feedback_type(system_mrl, self.correct_mrl)


@current_app.route('/feedback/create', methods=['POST'])
def create_feedback():
    form = FeedbackCreateForm()
    if form.validate_on_submit():
        data = form.get_data(exclude=['csrf_token'])
        feedback = {}
        if current_user.is_authenticated:
            feedback['user_id'] = current_user.id

        if data.get('model'):
            feedback['model'] = data['model']
        else:
            feedback['train_model'] = current_app.config['CURRENT_MODEL']
            feedback['model'] = ''

        # TODO: Do these things in form.
        nl = data['nl'].strip()
        feedback['nl'] = nl

        if data['systemMrl']:
            system_mrl = delete_spaces(data['systemMrl'])
            system_lin = linearise(system_mrl) or ''
        else:
            system_lin = ''
        feedback['system_lin'] = system_lin

        if data['correctMrl']:
            correct_mrl = delete_spaces(data['correctMrl'])
            correct_lin = linearise(correct_mrl) or ''
        else:
            correct_lin = ''
        feedback['correct_lin'] = correct_lin

        if data.get('parent_id'):
            try:
                feedback['parent_id'] = int(data['parent_id'])
            except ValueError:
                pass

        current_app.logger.info(
            'Received feedback: {}. Converted to feedback: {}'.format(data, feedback))

        url = current_app.config['JOEY_SERVER_URL'] + 'save_feedback'
        response = requests.post(url, json=feedback)
        return jsonify(response.json()), response.status_code

    return 'Bad Request', 400


@current_app.route('/export_feedback', methods=['GET'])
@login_required
def export_feedback():
    pass


@current_app.route('/feedback/<id>', methods=['GET', 'POST'])
@login_required
def feedback_piece(id):
    try:
        id = int(id)
    except ValueError:
        return 'Bad Request', 400

    form = FeedbackEditForm()

    if request.method =='POST':
        if form.validate_on_submit():
            payload = {'id': id}
            if not current_user.admin:
                payload['editor_id'] = current_user.id

            payload['correct_lin'] = (linearise(form.correct_mrl.data)
                                      if form.correct_mrl.data else '')
            payload['nl'] = form.nl.data

            url = current_app.config['JOEY_SERVER_URL'] + 'edit_feedback'
            response = requests.post(url, json=payload)
            if not response.ok:
                abort(response.status_code)
            info = response.json()
        else:
            return 'Bad Request', 400
    else:
        payload = {'id': id}
        if not current_user.admin:
            payload['querier_id'] = current_user.id
        url = current_app.config['JOEY_SERVER_URL'] + 'get_feedback'
        response = requests.post(url, json=payload)
        if not response.ok:
            abort(response.status_code)
        info = response.json()

    del info['created']
    info['model_lin'] = info.pop('system_lin')
    piece = FeedbackPiece(**info)
    form = FeedbackEditForm(obj=piece)

    return render_template('feedback.html', form=form, piece=piece)


@current_app.route('/feedback/<id>/delete', methods=['GET'])
@login_required
def delete_feedback_piece(id):
    try:
        id = int(id)
    except ValueError:
        return 'Bad Request', 400

    payload = {'id': id}
    if not current_user.admin:
        payload['editor_id'] = current_user.id

    url = current_app.config['JOEY_SERVER_URL'] + 'delete_feedback'
    response = requests.post(url, json=payload)

    if response.ok:
        current_app.logger.info('Deleted feedback with id {}'.format(id))
    else:
        try:
            error = response.json().get('error', None)
        except:
            error = None
        current_app.logger.error(
            'Failed deleting feedback with id {}.'
            ' Status Code: {}. Error: {}.'
            .format(id, response.status_code, error)
        )

    return redirect(url_for('list_feedback'))


@current_app.route('/feedback/list', methods=['GET'])
@login_required
def list_feedback():
    filters = {}
    if current_user.admin:
        parsing_model_form = AdminParsingModelForm(request.args)
        try:
            user_id = int(parsing_model_form.user.data)
        except (TypeError, ValueError):
            user_id = None
        else:
            if user_id < 0:
                user_id = None
    else:
        parsing_model_form = ParsingModelForm(request.args)
        user_id = current_user.id

    if parsing_model_form.model.data:
        model = parsing_model_form.model.data
    else:
        model = current_app.config['CURRENT_MODEL']
        parsing_model_form.model.process_data(model)

    filters = {'model': model}
    if user_id is not None:
        filters['user_id'] = user_id

    url = current_app.config['JOEY_SERVER_URL'] + 'query_feedback'

    response = requests.post(url, json=filters)
    feedback_by_id = {piece_data['id']: FeedbackPiece(**piece_data)
                      for piece_data in response.json()}

    if model:
        unparsed_queries = sum(piece.model_mrl is None
                               for piece in feedback_by_id.values())
    else:
        unparsed_queries = None

    feedback = []
    for piece in feedback_by_id.values():
        if piece.parent_id:
            if piece.parent_id in feedback_by_id:
                feedback_by_id[piece.parent_id].children.append(piece)
            else:
                current_app.logger.warning(
                    'Parent not found for feedback with id {}.'
                    .format(piece.id))
        else:
            feedback.append(piece)

    feedback_create_form = FeedbackCreateForm()

    return render_template(
        'list_feedback.html',
        parsing_model_form=parsing_model_form, model=model, feedback=feedback,
        unparsed_queries=unparsed_queries, current_user=current_user,
        feedback_create_form=feedback_create_form
    )


@current_app.route('/feedback/check', methods=['GET'])
@login_required
def check_feedback_states():
    form = ParsingModelForm(request.args)
    model = form.model.data or current_app.config['CURRENT_MODEL']
    filters = {'model': model, 'user_id': current_user.id}
    url = current_app.config['JOEY_SERVER_URL'] + 'query_feedback'
    response = requests.post(url, json=filters)
    if not response.ok:
        return jsonify({'error': 'Error in parsing server'}), 500

    feedback_states = {
        state.feedback_id: state
        for state in FeedbackState.query.filter_by(model=model)
    }
    response_data = {'learned': [], 'unlearned': []}
    for piece_data in response.json():
        id_ = piece_data['id']
        state = feedback_states.get(id_)
        if not piece_data['model_lin'] or not piece_data['correct_lin']:
            pass
        elif piece_data['correct_lin'] == piece_data['model_lin']:
            if state:
                if not state.correct:
                    state.correct = True
                    id_nl = {'id': id_, 'nl': piece_data['nl']}
                    response_data['learned'].append(id_nl)
                    db.session.add(state)
            else:
                feedback_states[id_] = new_state = FeedbackState(
                    feedback_id=id_, model=model, correct=True)
                db.session.add(new_state)
        else:
            if state:
                if state.correct:
                    state.correct = False
                    id_nl = {'id': id_, 'nl': piece_data['nl']}
                    response_data['unlearned'].append(id_nl)
                    db.session.add(state)
            else:
                feedback_states[id_] = new_state = FeedbackState(
                    feedback_id=id_, model=model, correct=False)
                db.session.add(new_state)

    db.session.commit()
    return jsonify(response_data)


@current_app.route('/update_parse_taggings', methods=['POST'])
def update_parse_taggings():
    pass
