from flask import current_app, render_template


@current_app.route('/available_tags', methods=['GET'])
def available_tags():
    return render_template('available_tags.html')
