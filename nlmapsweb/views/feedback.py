from collections import Counter, namedtuple
from io import BytesIO
from zipfile import ZipFile

from flask import (current_app, jsonify, redirect, render_template, request,
                   send_file, url_for)

from nlmapsweb.app import db
from nlmapsweb.models import Feedback, ParseLog, ParseTagging, Tag
from nlmapsweb.processing.converting import linearise
from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes
from nlmapsweb.forms.parse_taggings import ParseTaggingForm
from nlmapsweb.forms.feedback import FeedbackForm
from nlmapsweb.forms.parsing_model import ParsingModelForm


FeedbackPiece = namedtuple(
    'FeedbackPiece',
    ('id', 'parse_log_id', 'nl', 'correctMrl', 'systemMrl', 'type',
     'opcodes_json')
)


@current_app.route('/feedback/<id>', methods=['GET', 'POST'])
def feedback_piece(id):
    piece = Feedback.query.get(id)
    form = FeedbackForm(obj=piece)
    if form.validate_on_submit():
        piece.nl = form.nl.data
        piece.systemMrl = form.systemMrl.data
        piece.correctMrl = form.correctMrl.data
        db.session.add(piece)
        db.session.commit()
        return redirect(url_for('feedback_piece', id=id))

    all_ids = [fp.id for fp in Feedback.query.all()]
    smaller_ids = [id for id in all_ids if id < piece.id]
    prev_id = max(smaller_ids) if smaller_ids else None
    larger_ids = [id for id in all_ids if id > piece.id]
    next_id = min(larger_ids) if larger_ids else None

    return render_template('feedback.html', piece=piece, form=form,
                           prev_id=prev_id, next_id=next_id)


@current_app.route('/feedback/<id>/delete', methods=['GET'])
def delete_feedback_piece(id):
    piece = Feedback.query.get(id)
    if piece:
        db.session.delete(piece)
        db.session.commit()

    all_ids = [fp.id for fp in Feedback.query.all()]
    larger_ids = [p_id for p_id in all_ids if p_id > id]
    next_id = min(larger_ids) if larger_ids else None
    if next_id:
        return redirect(url_for('feedback_piece', id=next_id))
    else:
        return redirect(url_for('list_feedback'))


@current_app.route('/feedback/list', methods=['GET'])
def list_feedback():
    parsing_model_form = ParsingModelForm(request.args)
    feedback = Feedback.query.all()
    tag_forms = None

    model = parsing_model_form.data['model']
    if model:
        pieces = []
        for fpiece in feedback:
            piece = {'id': fpiece.id, 'nl': fpiece.nl,
                     'correctMrl': fpiece.correctMrl}
            parse_log = ParseLog.query.filter(
                ParseLog.model == model, ParseLog.nl == fpiece.nl
            ).first()

            if parse_log:
                piece['parse_log_id'] = parse_log.id
                piece['systemMrl'] = parse_log.mrl
                piece['opcodes_json'] = get_opcodes(
                    parse_log.mrl, fpiece.correctMrl, as_json=True)
                piece['type'] = get_feedback_type(parse_log.mrl,
                                                  fpiece.correctMrl)
            else:
                piece['parse_log_id'] = None
                piece['opcodes_json'] = 'null'
                piece['type'] = 'unparsed'
                piece['systemMrl'] = None

            pieces.append(FeedbackPiece(**piece))
        feedback = pieces

        tag_forms = {
            piece.id: ParseTaggingForm(feedback_id=piece.id,
                                       parse_log_id=piece.parse_log_id)
            for piece in feedback
            if piece.type == 'incorrect'
        }

    stats = Counter(piece.type for piece in feedback)
    return render_template(
        'list_feedback.html', feedback=feedback, model=model,
        parsing_model_form=parsing_model_form, stats=stats,
        tag_forms=tag_forms
    )

    #if request.args.get('types'):
    #    types = {type.strip() for type in request.args.get('types').split(',')}
    #    feedback = [piece for piece in feedback if piece.type in types]

    #if request.args.get('tags'):
    #    tags = {tag.strip() for tag in request.args.get('tags').split(',')}
    #    feedback = [piece for piece in feedback if tags.intersection([tag.name for tag in piece.tags])]

    #if request.args.get('untagged'):
    #    feedback = [piece for piece in feedback if not piece.tags]


@current_app.route('/update_parse_taggings', methods=['POST'])
def update_parse_taggings():
    form = ParseTaggingForm()
    if form.validate_on_submit():
        new_tag_names = form.new_tags.data
        for new_tag_name in new_tag_names:
            db.session.add(Tag(name=new_tag_name))

        feedback_id = int(form.feedback_id.data)
        parse_log_id = int(form.parse_log_id.data)

        given_tag_ids = db.session.query(ParseTagging.tag_id).filter(
            ParseTagging.feedback_id == feedback_id,
            ParseTagging.parse_log_id == parse_log_id,
        )
        given_tags = Tag.query.filter(Tag.id.in_(given_tag_ids))
        given_tag_names = [tag.name for tag in given_tags]
        target_tag_names = form.tags.data + new_tag_names

        tag_ids_to_delete = [tag.id for tag in given_tags
                             if tag.name not in target_tag_names]
        tag_names_to_add = [tag_name for tag_name in target_tag_names
                            if tag_name not in given_tag_names]
        tag_ids_to_add = [
            row[0] for row
            in db.session.query(Tag.id).filter(Tag.name.in_(tag_names_to_add))
        ]

        for pt in ParseTagging.query.filter(
                ParseTagging.tag_id.in_(tag_ids_to_delete)).all():
            db.session.delete(pt)

        for tag_id in tag_ids_to_add:
            pt = ParseTagging(parse_log_id=parse_log_id,
                              feedback_id=feedback_id, tag_id=tag_id)
            db.session.add(pt)
        db.session.commit()

        return jsonify({'newTags': new_tag_names})

    return 'Bad Request', 400


@current_app.route('/export_feedback', methods=['GET'])
def export_feedback():
    feedback = Feedback.query.all()

    english = []
    system = []
    correct = []
    system_lin = []
    correct_lin = []
    for piece in feedback:
        if piece.correctMrl:
            english.append(piece.nl)
            correct.append(piece.correctMrl)
            correct_lin.append(linearise(piece.correctMrl) or '')
            if piece.systemMrl:
                system.append(piece.systemMrl)
                system_lin.append(linearise(piece.systemMrl) or '')
            else:
                system.append('')
                system_lin.append('')

    # Append empty string so that joining will yield a trailing newline.
    english.append('')
    system.append('')
    correct.append('')
    system_lin.append('')
    correct_lin.append('')

    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zf:
        zf.writestr('nlmaps_web/nlmaps.web.en', '\n'.join(english))
        zf.writestr('nlmaps_web/nlmaps.web.correct.mrl', '\n'.join(correct))
        zf.writestr('nlmaps_web/nlmaps.web.correct.lin', '\n'.join(correct_lin))
        zf.writestr('nlmaps_web/nlmaps.web.system.mrl', '\n'.join(system))
        zf.writestr('nlmaps_web/nlmaps.web.system.lin', '\n'.join(system_lin))
    memory_file.seek(0)

    return send_file(
        memory_file, attachment_filename='nlmaps_web.zip',
                     mimetype='application/zip', as_attachment=True)
