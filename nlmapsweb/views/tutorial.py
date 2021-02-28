from flask import current_app, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from nlmapsweb.tutorial import CHAPTERS, get_user_chapter, set_user_chapter


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
