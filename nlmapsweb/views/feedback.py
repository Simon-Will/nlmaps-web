from flask_login import current_user
from flask import current_app, request, render_template
import requests

from nlmapsweb.forms import AdminParsingModelForm, FeedbackForm, ParsingModelForm
from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes
from nlmapsweb.processing.converting import delete_spaces, functionalise, linearise


def get_lin_and_mrl(lin, mrl):
    if lin and not mrl:
        mrl = functionalise(lin)
    elif mrl and not lin:
        lin = functionalise(mrl)
    return lin, mrl


class FeedbackPiece:

    def __init__(self, nl, id=None, parent_id=None, model=None,
                 correct_lin=None, correct_mrl=None, original_model=None,
                 original_lin=None, original_mrl=None, model_lin=None,
                 model_mrl=None):
        self.nl = nl
        self.id = id
        self.parent_id = parent_id
        self.model = model

        self.correct_lin, self.correct_mrl = get_lin_and_mrl(
            correct_lin, correct_mrl)
        if not self.correct_mrl:
            raise ValueError(
                'FeedbackPiece must have a correct_mrl, but it is None')

        self.original_lin, self.original_mrl = get_lin_and_mrl(
            original_lin, original_mrl)
        self.model_lin, self.model_mrl = get_lin_and_mrl(
            model_lin, model_mrl)

    def get_opcodes(self, model=True, as_json=True):
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_opcodes(system_mrl, self.correct_mrl, as_json=as_json)

    def get_type(self, model=True):
        system_mrl = self.model_mrl if model else self.original_mrl
        return get_feedback_type(system_mrl, self.correct_mrl)


@current_app.route('/feedback/create', methods=['POST'])
def create_feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        data = form.get_data(exclude=['csrf_token'])
        feedback = {}
        if current_user.is_authenticated:
            feedback['user_id'] = current_user.id

        feedback['model'] = data['model']

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

        current_app.logger.info(
            'Received feedback: {}. Converted to feedback: {}'.format(data, feedback))

        url = current_app.config['JOEY_SERVER_URL'] + 'save_feedback'
        requests.post(url, json=feedback)

        return 'OK', 200

    return 'Bad Request', 400


@current_app.route('/export_feedback', methods=['GET'])
def export_feedback():
    pass

@current_app.route('/feedback/<id>', methods=['GET', 'POST'])
def feedback_piece(id):
    pass

@current_app.route('/feedback/list', methods=['GET'])
def list_feedback():
    filters = {}
    if current_user.admin:
        parsing_model_form = AdminParsingModelForm(request.args)
        user_id = parsing_model_form.user.data
        if user_id and user_id < 0:
            user_id = None
    else:
        parsing_model_form = ParsingModelForm(request.args)
        user_id = current_user.id

    model = parsing_model_form.model.data or current_app.config['CURRENT_MODEL']
    filters = {'model': model}

    url = current_app.config['JOEY_SERVER_URL'] + 'query_feedback'

    response = requests.post(url, json=filters)
    feedback = [FeedbackPiece(**piece_data) for piece_data in response.json()]

    return render_template('list_feedback.html',
        parsing_model_form=parsing_model_form, model=model, feedback=feedback
    )

@current_app.route('/update_parse_taggings', methods=['POST'])
def update_parse_taggings():
    pass

#from collections import Counter, defaultdict, namedtuple
#from io import BytesIO
#from zipfile import ZipFile
#
#from flask import (abort, current_app, jsonify, redirect, render_template,
#                   request, send_file, url_for)
#
#from nlmapsweb.app import db
#from nlmapsweb.models import Feedback, ParseLog, ParseTagging, Tag
#from nlmapsweb.processing.converting import linearise
#from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes
#from nlmapsweb.forms.parse_taggings import ParseTaggingForm
#from nlmapsweb.forms.feedback import FeedbackExportForm, FeedbackForm
#from nlmapsweb.forms.parsing_model import ParsingModelForm
#from nlmapsweb.utils.plotting import fig_to_base64, plot_tagged_percentages
#
#
#FeedbackPiece = namedtuple(
#    'FeedbackPiece',
#    ('id', 'parse_log_id', 'nl', 'correctMrl', 'systemMrl', 'type',
#     'opcodes_json')
#)
#
#
#def get_model_bound_feedback(model, feedback):
#    pieces = []
#    for fpiece in feedback:
#        piece = {'id': fpiece.id, 'nl': fpiece.nl,
#                 'correctMrl': fpiece.correctMrl}
#        parse_log = ParseLog.query.filter(
#            ParseLog.model == model, ParseLog.nl == fpiece.nl
#        ).first()
#
#        if parse_log:
#            piece['parse_log_id'] = parse_log.id
#            piece['systemMrl'] = parse_log.mrl
#            piece['opcodes_json'] = get_opcodes(
#                parse_log.mrl, fpiece.correctMrl, as_json=True)
#            piece['type'] = get_feedback_type(parse_log.mrl,
#                                              fpiece.correctMrl)
#        else:
#            piece['parse_log_id'] = None
#            piece['opcodes_json'] = 'null'
#            piece['type'] = 'unparsed'
#            piece['systemMrl'] = None
#
#        pieces.append(FeedbackPiece(**piece))
#    return pieces
#
#
#@current_app.route('/feedback/<id>', methods=['GET', 'POST'])
#def feedback_piece(id):
#    try:
#        id = int(id)
#    except ValueError:
#        abort(404)
#
#    piece = Feedback.query.get(id)
#    if not piece:
#        abort(404)
#
#    form = FeedbackForm(obj=piece)
#    if form.validate_on_submit():
#        piece.nl = form.nl.data
#        piece.systemMrl = form.systemMrl.data
#        piece.correctMrl = form.correctMrl.data
#        db.session.add(piece)
#        db.session.commit()
#        return redirect(url_for('feedback_piece', id=id))
#
#    all_ids = [fp.id for fp in Feedback.query.all()]
#    smaller_ids = [id for id in all_ids if id < piece.id]
#    prev_id = max(smaller_ids) if smaller_ids else None
#    larger_ids = [id for id in all_ids if id > piece.id]
#    next_id = min(larger_ids) if larger_ids else None
#
#    return render_template('feedback.html', piece=piece, form=form,
#                           prev_id=prev_id, next_id=next_id)
#
#
#@current_app.route('/feedback/<id>/delete', methods=['GET'])
#def delete_feedback_piece(id):
#    try:
#        id = int(id)
#    except ValueError:
#        abort(404)
#
#    piece = Feedback.query.get(id)
#    if not piece:
#        abort(404)
#
#    if piece:
#        db.session.delete(piece)
#        db.session.commit()
#
#    all_ids = [fp.id for fp in Feedback.query.all()]
#    larger_ids = [p_id for p_id in all_ids if p_id > id]
#    next_id = min(larger_ids) if larger_ids else None
#    if next_id:
#        return redirect(url_for('feedback_piece', id=next_id))
#    else:
#        return redirect(url_for('list_feedback'))
#
#
#@current_app.route('/feedback/list', methods=['GET'])
#def list_feedback():
#    parsing_model_form = ParsingModelForm(request.args)
#    feedback = Feedback.query.all()
#    tag_forms = None
#    tag_plot_b64 = None
#    tag_count_stats = None
#
#    model = parsing_model_form.data['model']
#    if model:
#        feedback = get_model_bound_feedback(model, feedback)
#
#        tag_forms = {
#            piece.id: ParseTaggingForm(feedback_id=piece.id,
#                                       parse_log_id=piece.parse_log_id)
#            for piece in feedback
#            if piece.type == 'incorrect'
#        }
#        tag_counts = {tag.name: 0 for tag in Tag.query.all()}
#        tag_counts.update(Counter(tag for tag_form in tag_forms.values()
#                                  for tag in tag_form.tags.data))
#        tag_plot = plot_tagged_percentages(tag_counts, total=len(feedback))
#        tag_plot_b64 = fig_to_base64(tag_plot, 'jpg')
#
#        tag_count_stats = defaultdict(lambda: 0)
#        for tag_form in tag_forms.values():
#            number_of_tags = len(tag_form.tags.data)
#            tag_count_stats[number_of_tags] += 1
#
#    absolute_stats = Counter(piece.type for piece in feedback)
#    total = len(feedback)
#    relative_stats = {type: count / total
#                      for type, count in absolute_stats.items()}
#    stats = {
#        'absolute': absolute_stats,
#        'relative': relative_stats,
#        'total': total,
#        'accuracy': absolute_stats.get('correct', 0) / total,
#    }
#
#    if request.args.get('types'):
#        types = {type.strip() for type in request.args.get('types').split(',')}
#        feedback = [piece for piece in feedback if piece.type in types]
#
#    #if request.args.get('tags'):
#    #    tags = {tag.strip() for tag in request.args.get('tags').split(',')}
#    #    feedback = [piece for piece in feedback if tags.intersection([tag.name for tag in piece.tags])]
#
#    if request.args.get('untagged'):
#        feedback = [piece for piece in feedback
#                    if piece.type == 'incorrect'
#                    and not tag_forms[piece.id].tags.data]
#
#    feedback_export_form = FeedbackExportForm()
#    if model:
#        feedback_export_form.model.process_data(model)
#
#    return render_template(
#        'list_feedback.html', feedback=feedback, model=model,
#        parsing_model_form=parsing_model_form, stats=stats,
#        tag_forms=tag_forms, tag_plot_b64=tag_plot_b64,
#        tag_count_stats=tag_count_stats,
#        feedback_export_form=feedback_export_form
#    )
#
#
#@current_app.route('/update_parse_taggings', methods=['POST'])
#def update_parse_taggings():
#    form = ParseTaggingForm()
#    if form.validate_on_submit():
#        new_tag_names = form.new_tags.data
#        for new_tag_name in new_tag_names:
#            db.session.add(Tag(name=new_tag_name))
#
#        feedback_id = int(form.feedback_id.data)
#        parse_log_id = int(form.parse_log_id.data)
#
#        given_tag_ids = db.session.query(ParseTagging.tag_id).filter(
#            ParseTagging.feedback_id == feedback_id,
#            ParseTagging.parse_log_id == parse_log_id,
#        )
#        given_tags = Tag.query.filter(Tag.id.in_(given_tag_ids))
#        given_tag_names = [tag.name for tag in given_tags]
#        target_tag_names = form.tags.data + new_tag_names
#
#        tag_ids_to_delete = [tag.id for tag in given_tags
#                             if tag.name not in target_tag_names]
#        tag_names_to_add = [tag_name for tag_name in target_tag_names
#                            if tag_name not in given_tag_names]
#        tag_ids_to_add = [
#            row[0] for row
#            in db.session.query(Tag.id).filter(Tag.name.in_(tag_names_to_add))
#        ]
#
#        for pt in ParseTagging.query.filter(
#                ParseTagging.feedback_id == feedback_id,
#                ParseTagging.parse_log_id == parse_log_id,
#                ParseTagging.tag_id.in_(tag_ids_to_delete)).all():
#            db.session.delete(pt)
#
#        for tag_id in tag_ids_to_add:
#            pt = ParseTagging(parse_log_id=parse_log_id,
#                              feedback_id=feedback_id, tag_id=tag_id)
#            db.session.add(pt)
#        db.session.commit()
#
#        return jsonify({'newTags': new_tag_names})
#
#    return 'Bad Request', 400
#
#
#@current_app.route('/export_feedback', methods=['GET'])
#def export_feedback():
#    feedback = Feedback.query.all()
#
#    form = FeedbackExportForm(request.args)
#    use_correct = form.correct.data
#    use_incorrect = form.incorrect.data
#
#    model = form.model.data
#    if model:
#        feedback = get_model_bound_feedback(model, feedback)
#
#    english = []
#    system = []
#    correct = []
#    system_lin = []
#    correct_lin = []
#    for piece in feedback:
#        is_correct = piece.type == 'correct'
#        if (is_correct and not use_correct
#                or not is_correct and not use_incorrect):
#            continue
#
#        if piece.correctMrl:
#            english.append(piece.nl)
#            correct.append(piece.correctMrl)
#            correct_lin.append(linearise(piece.correctMrl) or '')
#            if piece.systemMrl:
#                system.append(piece.systemMrl)
#                system_lin.append(linearise(piece.systemMrl) or '')
#            else:
#                system.append('')
#                system_lin.append('')
#
#    # Append empty string so that joining will yield a trailing newline.
#    english.append('')
#    system.append('')
#    correct.append('')
#    system_lin.append('')
#    correct_lin.append('')
#
#    memory_file = BytesIO()
#    with ZipFile(memory_file, 'w') as zf:
#        zf.writestr('nlmaps_web/nlmaps.web.en', '\n'.join(english))
#        zf.writestr('nlmaps_web/nlmaps.web.correct.mrl', '\n'.join(correct))
#        zf.writestr('nlmaps_web/nlmaps.web.correct.lin', '\n'.join(correct_lin))
#        zf.writestr('nlmaps_web/nlmaps.web.system.mrl', '\n'.join(system))
#        zf.writestr('nlmaps_web/nlmaps.web.system.lin', '\n'.join(system_lin))
#    memory_file.seek(0)
#
#    return send_file(
#        memory_file, attachment_filename='nlmaps_web.zip',
#        mimetype='application/zip', as_attachment=True
#    )
