from flask import current_app, render_template


@current_app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
