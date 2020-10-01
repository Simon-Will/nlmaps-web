from collections import Counter
from io import BytesIO
from zipfile import ZipFile

from flask import current_app, render_template, send_file

from nlmapsweb.app import db
from nlmapsweb.models import Feedback
from nlmapsweb.processing.converting import linearise


@current_app.route('/list_feedback', methods=['GET'])
def list_feedback():
    feedback = db.session.query(Feedback).all()
    stats = Counter(piece.type for piece in feedback)

    return render_template('feedback.html', feedback=feedback, stats=stats)


@current_app.route('/export_feedback', methods=['GET'])
def export_feedback():
    feedback = db.session.query(Feedback).all()

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
