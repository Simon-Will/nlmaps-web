from flask import current_app, render_template


@current_app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')


@current_app.route('/guidelines', methods=['GET'])
def guidelines():
    return render_template('guidelines.html')


@current_app.route('/osm_tags', methods=['GET'])
def osm_tags():
    return render_template('osm_tags.html')

