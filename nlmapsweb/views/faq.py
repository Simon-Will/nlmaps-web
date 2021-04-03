from flask import current_app, render_template


@current_app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')
