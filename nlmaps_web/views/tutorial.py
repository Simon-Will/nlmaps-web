from flask import (current_app, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from nlmaps_web.app import db
from nlmaps_web.models import TutorialFeedback
from nlmaps_web.tutorial import CHAPTERS, get_user_chapter, set_user_chapter
from nlmaps_web.utils.auth import admin_required


@current_app.route('/tutorial', methods=['GET'])
def tutorial():
    """Serve a tutorial page.

    The GET argument 'chapter' determines which chapter to view, with 1 being
    the first actual chapter and 0 being an info page for unauthenticated users
    visiting the tutorial for he first time.

    See the tutorial.py file for more information about how the tutorial works.
    """
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
    """Common endpoint for listing and creating feedback for the tutorial.

    This view for splitting GET and POST is used so we can use the
    @admin_required decorator for the viewing part.
    """
    if request.method == 'POST':
        return post_tutorial_feedback()
    else:
        return get_tutorial_feedback()


def post_tutorial_feedback():
    """Create feedback for the tutorial."""
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
    """List all feedback given for the tutorial."""
    feedback = list(TutorialFeedback.query.all())
    return render_template('tutorial_feedback.html', feedback=feedback)
