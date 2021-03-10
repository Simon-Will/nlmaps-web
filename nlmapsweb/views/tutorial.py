from flask import (current_app, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from nlmapsweb.app import db
from nlmapsweb.models import TutorialFeedback
from nlmapsweb.tutorial import CHAPTERS, get_user_chapter, set_user_chapter
from nlmapsweb.utils.auth import admin_required


@current_app.route('/tutorial', methods=['GET'])
def tutorial():
    if request.args.get('no_login'):
        set_user_chapter(chapter_finished=0)

    user_chapter = get_user_chapter()
    if user_chapter < 0:
        max_chapter = len(CHAPTERS)
    else:
        max_chapter = user_chapter

    try:
        chapter = int(request.args.get('chapter', max_chapter))
    except (ValueError, TypeError):
        chapter = max_chapter

    if chapter > max_chapter:
        return redirect(url_for('tutorial'))

    chapter_title = ('Cookie Information' if chapter == 0
                     else CHAPTERS[chapter - 1])
    toc = CHAPTERS
    return render_template(
        'tutorial.html', chapter=chapter, max_chapter=max_chapter,
        chapter_title=chapter_title, toc=toc
    )


@current_app.route('/tutorial_feedback', methods=['GET', 'POST'])
def tutorial_feedback():
    if request.method == 'POST':
        return post_tutorial_feedback()
    else:
        return get_tutorial_feedback()


def post_tutorial_feedback():
    feedback = request.form.get('feedback')
    if feedback:
        current_app.logger.info('Received tutorial feedback.')
        tfb = TutorialFeedback(content=feedback[:2000])
        db.session.add(tfb)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'error': 'No “feedback” in POST payload'}), 400


@admin_required
def get_tutorial_feedback():
    feedback = list(TutorialFeedback.query.all())
    return render_template('tutorial_feedback.html', feedback=feedback)
