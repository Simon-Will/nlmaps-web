from collections import Counter
from io import BytesIO
from zipfile import ZipFile

from flask import (current_app, jsonify, redirect, render_template, request,
                   send_file, url_for)

from nlmapsweb.app import db
from nlmapsweb.models import Feedback, Tag
from nlmapsweb.processing.converting import linearise
from nlmapsweb.forms.tags import FeedbackTagsForm
from nlmapsweb.forms.feedback import FeedbackForm


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


@current_app.route('/list_feedback', methods=['GET'])
def list_feedback():
    feedback = Feedback.query.all()
    stats = Counter(piece.type for piece in feedback)

    tag_forms = {
        piece.id: FeedbackTagsForm(feedback_piece=piece)
        for piece in feedback
        if piece.type == 'incorrect'
    }

    if request.args.get('types'):
        types = {type.strip() for type in request.args.get('types').split(',')}
        feedback = [piece for piece in feedback if piece.type in types]

    if request.args.get('tags'):
        tags = {tag.strip() for tag in request.args.get('tags').split(',')}
        feedback = [piece for piece in feedback if tags.intersection([tag.name for tag in piece.tags])]

    if request.args.get('untagged'):
        feedback = [piece for piece in feedback if not piece.tags]

    return render_template('list_feedback.html', feedback=feedback,
                           tag_forms=tag_forms, stats=stats)


@current_app.route('/tag_feedback', methods=['POST'])
def tag_feedback():
    form = FeedbackTagsForm()
    if form.validate_on_submit():
        new_tag_names = form.new_tags.data
        for new_tag_name in new_tag_names:
            db.session.add(Tag(name=new_tag_name))

        feedback_piece = Feedback.query.get(form.feedback_id.data)
        tag_names = form.tags.data + new_tag_names
        tags = [tag for tag in Tag.query.all() if tag.name in tag_names]
        feedback_piece.tags = tags
        db.session.add(feedback_piece)
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
