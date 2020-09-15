from collections import Counter

from flask import current_app, render_template

from nlmapsweb.app import db
from nlmapsweb.models import Feedback


@current_app.route('/list_feedback', methods=['GET'])
def list_feedback():
    feedback = db.session.query(Feedback).all()
    stats = Counter(piece.type for piece in feedback)

    return render_template('feedback.html', feedback=feedback, stats=stats)
