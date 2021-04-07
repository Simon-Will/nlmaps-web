from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile

from flask_login import current_user, login_required
from flask import (abort, current_app, jsonify, redirect, render_template,
                   request, send_file, url_for)

from nlmapsweb.app import db
from nlmapsweb.forms import (AdminFeedbackListForm, FeedbackCreateForm,
                             FeedbackEditForm, FeedbackListForm)
from nlmapsweb.models import FeedbackState, NameOccurrence
import nlmapsweb.mt_server as mt_server
from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes
from nlmapsweb.processing.converting import functionalise, linearise
from nlmapsweb.processing.replacing import increment_name_occurrences, replace_feedback
from nlmapsweb.tutorial import tutorial_dummy_saver
from nlmapsweb.utils.auth import admin_required
from nlmapsweb.utils.paging import make_paging_info


def get_lin_and_mrl(lin, mrl):
    """Complete lin, mrl combo as well as possible."""
    if lin and not mrl:
        mrl = functionalise(lin)
    elif mrl and not lin:
        lin = functionalise(mrl)
    return lin, mrl


class FeedbackPiece:
    """Representation of a piece of feedback

    The feedback resides in the database of the machine translation server.
    This is a mirror that provides the MRLs in addition to the LIN query.

    correct_{lin,mrl}: The correct query as given by the user feedback
    original_{lin,mrl}: The query as originally parsed by the server
    model_{lin,mrl}: The query as recently parsed by the server
    """

    def __init__(self, nl, id=None, created=None, parent_id=None, user_id=None,
                 model=None, correct_lin=None, correct_mrl=None,
                 original_model=None, original_lin=None, original_mrl=None,
                 model_lin=None, model_mrl=None, children=None, split=None):
        self.nl = nl
        self.id = id
        self.created = created
        self.parent_id = parent_id
        self.user_id = user_id
        self.model = model
        self.original_model = original_model

        self.correct_lin, self.correct_mrl = get_lin_and_mrl(
            correct_lin, correct_mrl)
        self.original_lin, self.original_mrl = get_lin_and_mrl(
            original_lin, original_mrl)
        self.model_lin, self.model_mrl = get_lin_and_mrl(
            model_lin, model_mrl)

        self.children = children or []

        self.split = split

    def get_opcodes(self, model=True, as_json=True):
        """Get opcodes to edit system MRL into correct MRL."""
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_opcodes(system_mrl, self.correct_mrl, as_json=as_json)

    def get_type(self, model=True):
        """Get correctness type of feedback type."""
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_feedback_type(system_mrl, self.correct_mrl)


@current_app.route('/feedback/create', methods=['POST'])
def create_feedback():
    """Create feedback at the machine translation server.

    Use by Ajax.
    """
    form = FeedbackCreateForm()
    if form.validate_on_submit():
        data = form.get_data(exclude=['csrf_token'])
        feedback = {}
        if current_user.is_authenticated:
            feedback['user_id'] = current_user.id

        feedback['train_model'] = current_app.config['CURRENT_MODEL']
        feedback['model'] = data.get('model', '')

        # TODO: Do these things in form.
        nl = data['nl'].strip()
        feedback['nl'] = nl

        if data['systemMrl']:
            system_mrl = data['systemMrl'].strip()
            system_lin = linearise(system_mrl) or ''
        else:
            system_lin = ''
        feedback['system_lin'] = system_lin

        if data['correctMrl']:
            correct_mrl = data['correctMrl'].strip()
            correct_lin = linearise(correct_mrl) or ''
        else:
            correct_mrl = ''
            correct_lin = ''
        feedback['correct_lin'] = correct_lin

        if data.get('parent_id'):
            try:
                feedback['parent_id'] = int(data['parent_id'])
            except ValueError:
                pass

        current_app.logger.info(
            'Received feedback: {}. Converted to feedback: {}'
            .format(data, feedback)
        )

        if feedback['model'] == 'tutorial':
            response_dict, status_code = tutorial_dummy_saver(feedback)
            return jsonify(response_dict), status_code

        if (current_app.config.get('REPLACE_DUPLICATE_NAMES')
            and feedback.get('user_id')):
            replacement, replaced_mrl = replace_feedback(feedback, correct_mrl,
                                                         feedback['user_id'])
        else:
            replacement = None

        if replacement:
            feedback['split'] = 'replaced'
            response = mt_server.post('save_feedback', json=feedback)
            returned_feedback = response.json()
            increment_name_occurrences(correct_mrl)

            if 'id' in returned_feedback:
                replacement['parent_id'] = returned_feedback['id']
                mt_server.post('save_feedback', json=replacement)
                increment_name_occurrences(replaced_mrl)
        else:
            response = mt_server.post('save_feedback', json=feedback)
            returned_feedback = response.json()
            increment_name_occurrences(correct_mrl)

        returned_feedback['correct_mrl'] = correct_mrl
        print('RESPONSE:', returned_feedback)
        return jsonify(returned_feedback), response.status_code

    return 'Bad Request', 400


@current_app.route('/replace_feedback/<id>', methods=['GET'])
@admin_required
def replace_feedback_view(id):
    try:
        id = int(id)
    except ValueError:
        return 'Bad Request', 400

    payload = {'id': id}
    response = mt_server.post('get_feedback', json=payload)
    if not response.ok:
        abort(response.status_code)
    feedback = response.json()
    correct_mrl = functionalise(feedback['correct_lin'])

    if not feedback.get('user_id'):
        return jsonify({'error': 'Feedback has no user id.'}), 500

    replacement, replaced_mrl = replace_feedback(feedback, correct_mrl,
                                                 feedback['user_id'])
    if replacement:
        replacement['parent_id'] = feedback['id']
        response = mt_server.post('save_feedback', json=replacement)
        if not response.ok:
            return jsonify({'error': 'Saving replacement failed.'}), 500
        returned_replacement = response.json()
        returned_replacement['correct_mrl'] = replaced_mrl

        response = mt_server.post(
            'edit_feedback',
            json={'id': feedback['id'], 'split': 'replaced'}
        )
        if not response.ok:
            return jsonify({'error':
                            'Editing original feedback’s split failed.'}), 500
        return jsonify(returned_replacement), 200
    else:
        return jsonify({'error': 'Generating replacement failed.'}), 500


@current_app.route('/export_feedback', methods=['GET'])
@login_required
def export_feedback():
    """Export feedback as a zip file of nlmaps dataset."""
    if current_user.admin:
        feedback_list_form = AdminFeedbackListForm(request.args)
        try:
            user_id = int(feedback_list_form.user.data)
        except (TypeError, ValueError):
            user_id = None
        else:
            if user_id < 0:
                user_id = None
    else:
        feedback_list_form = FeedbackListForm(request.args)
        user_id = current_user.id

    filters = {'model': current_app.config['CURRENT_MODEL']}
    if user_id is not None:
        filters['user_id'] = user_id

    response = mt_server.post('query_feedback', json=filters)
    feedback = [FeedbackPiece(**data) for data in response.json()['feedback']]

    independent_feedback = []
    parent_to_children = defaultdict(list)
    for piece in feedback:
        if piece.parent_id:
            parent_to_children[piece.parent_id].append(piece)
        else:
            independent_feedback.append(piece)

    nl = []
    lin = []
    mrl = []

    def append_piece(piece):
        if piece.nl and piece.correct_lin and piece.correct_mrl:
            nl.append(piece.nl)
            lin.append(piece.correct_lin)
            mrl.append(piece.correct_mrl)

    for parent in independent_feedback:
        append_piece(parent)
        for child in parent_to_children[parent.id]:
            append_piece(child)

    # Append empty string so that joining will yield a trailing newline.
    nl.append('')
    lin.append('')
    mrl.append('')

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:
        zf.writestr('nlmaps_web/nlmaps.web.en', '\n'.join(nl))
        zf.writestr('nlmaps_web/nlmaps.web.lin', '\n'.join(lin))
        zf.writestr('nlmaps_web/nlmaps.web.mrl', '\n'.join(mrl))
    memory_file.seek(0)

    return send_file(
        memory_file, attachment_filename='nlmaps_web.zip',
        mimetype='application/zip', as_attachment=True
    )


@current_app.route('/feedback/<id>', methods=['GET', 'POST'])
@login_required
def feedback_piece(id):
    """Display/Edit a single piece of feedback."""
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

            response = mt_server.post('edit_feedback', json=payload)
            if not response.ok:
                abort(response.status_code)
            info = response.json()
        else:
            return 'Bad Request', 400
    else:
        payload = {'id': id}
        if not current_user.admin:
            payload['querier_id'] = current_user.id
        response = mt_server.post('get_feedback', json=payload)
        if not response.ok:
            abort(response.status_code)
        info = response.json()

    info['model_lin'] = info.pop('system_lin')
    piece = FeedbackPiece(**info)
    form = FeedbackEditForm(obj=piece)

    return render_template('feedback.html', form=form, piece=piece)


@current_app.route('/feedback/<id>/delete', methods=['GET'])
@login_required
def delete_feedback_piece(id):
    """Delete a feedback piece."""
    try:
        id = int(id)
    except ValueError:
        return 'Bad Request', 400

    payload = {'id': id}
    if not current_user.admin:
        payload['editor_id'] = current_user.id

    response = mt_server.post('delete_feedback', json=payload)

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
    """List all pieces of feedback for one or all users."""
    if current_user.admin:
        feedback_list_form = AdminFeedbackListForm(request.args)
        try:
            user_id = int(feedback_list_form.user.data)
        except (TypeError, ValueError):
            user_id = None
        else:
            if user_id < 0:
                user_id = None
    else:
        feedback_list_form = FeedbackListForm(request.args)
        user_id = current_user.id

    if feedback_list_form.model.data:
        model = feedback_list_form.model.data
    else:
        model = current_app.config['CURRENT_MODEL']
        feedback_list_form.model.process_data(model)

    try:
        page = int(feedback_list_form.page.data)
    except (TypeError, ValueError):
        page = 1
        feedback_list_form.page.process_data(page)

    page_size = current_app.config.get('FEEDBACK_PAGE_SIZE', 50)
    offset = (page - 1) * page_size

    filters = {'model': model, 'offset': offset, 'limit': page_size}
    if user_id is not None:
        filters['user_id'] = user_id

    response = mt_server.post('query_feedback', json=filters)
    response_data = response.json()
    feedback_objects = response_data['feedback']
    total_count = response_data['total_count']
    paging_info = make_paging_info(
        current_page=page, page_size=page_size, object_count=total_count,
        view_name='list_feedback', request_args=request.args
    )

    feedback = [FeedbackPiece(**piece_data)
                for piece_data in feedback_objects]

    if model:
        unparsed_queries = sum(piece.model_mrl is None for piece in feedback)
    else:
        unparsed_queries = None

    feedback_create_form = FeedbackCreateForm()

    return render_template(
        'list_feedback.html',
        feedback_list_form=feedback_list_form, model=model, feedback=feedback,
        unparsed_queries=unparsed_queries, current_user=current_user,
        feedback_create_form=feedback_create_form, paging_info=paging_info
    )


@current_app.route('/feedback/check', methods=['GET'])
@login_required
def check_feedback_states():
    """Check if model parses of feedback changed.

    This view is for checking if a saved feedback query that was previously
    parsed correctly is now parsed incorrectly, or vice versa.

    This is done by saving the last state (correct/incorrect) for each feedback
    locally and comparing it to the current state at the machine translation
    server. The local last state is also updated during the process.

    Use by Ajax.
    """
    form = FeedbackListForm(request.args)
    model = form.model.data or current_app.config['CURRENT_MODEL']
    filters = {'model': model, 'user_id': current_user.id}
    response = mt_server.post('query_feedback', json=filters)
    if not response.ok:
        return jsonify({'error': 'Error in parsing server'}), 500

    feedback_states = {
        state.feedback_id: state
        for state in FeedbackState.query.filter_by(model=model)
    }
    response_data = {'learned': [], 'unlearned': []}
    for piece_data in response.json()['feedback']:
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


@current_app.route('/reset_name_occurrences', methods=['GET'])
@admin_required
def reset_name_occurrences():
    response = mt_server.post('list_feedback', json={})

    NameOccurrence.query.delete()
    for piece in response.json():
        if piece['correct_lin'] and piece['user_id']:
            correct_mrl = functionalise(piece['correct_lin'])
            if correct_mrl:
                increment_name_occurrences(correct_mrl, piece['user_id'])

    return jsonify({'success': True})


@current_app.route('/replace_existing_feedback', methods=['GET'])
@admin_required
def replace_existing_feedback():
    response = mt_server.post('list_feedback', json={})
    replaced_count = 0
    NameOccurrence.query.delete()
    for piece in response.json():
        if piece['user_id']:
            correct_mrl = functionalise(piece['correct_lin'])
            if not correct_mrl:
                continue

            if (not piece['split'] or 'replaced' in piece['split']
                    or piece['parent_id']):
                increment_name_occurrences(correct_mrl, piece['user_id'])
                continue

            replacement, replaced_mrl = replace_feedback(piece, correct_mrl,
                                                         piece['user_id'])
            if not replacement:
                increment_name_occurrences(correct_mrl, piece['user_id'])
                continue

            replacement['parent_id'] = piece['id']
            response = mt_server.post('save_feedback',
                                      json=replacement)
            if not response.ok:
                msg = ('Saving replacement {} for feedback {} failed.'
                       .format(replacement, piece))
                current_app.logger.warning(msg)
                return jsonify({'error': msg}), 500

            increment_name_occurrences(replaced_mrl, piece['user_id'])

            response = mt_server.post(
                'edit_feedback',
                json={'id': piece['id'], 'split': 'replaced'}
            )
            if not response.ok:
                msg = (
                    'Editing original feedback’s split failed. Feedback: {}'
                    .format(piece)
                )
                current_app.logger.warning(msg)
                return jsonify({'error': msg}), 500
            increment_name_occurrences(correct_mrl, piece['user_id'])

            replaced_count += 1
    return jsonify({'replaced': replaced_count})


@current_app.route('/update_parse_taggings', methods=['POST'])
def update_parse_taggings():
    pass
