from flask import current_app, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from nlmapsweb.tutorial import CHAPTERS


@current_app.route('/tutorial', methods=['GET'])
@login_required
def tutorial():
    if current_user.tutorial_chapter < 1:
        max_chapter = len(CHAPTERS)
    else:
        max_chapter = current_user.tutorial_chapter

    try:
        chapter = int(request.args.get('chapter', max_chapter))
    except (ValueError, TypeError):
        chapter = max_chapter

    if chapter > max_chapter:
        return redirect(url_for('tutorial'))

    toc = CHAPTERS
    return render_template(
        'tutorial.html', chapter=chapter, max_chapter=max_chapter, toc=toc
    )
