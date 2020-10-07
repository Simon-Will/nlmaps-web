from flask import current_app, render_template


@current_app.route('/osm_tags', methods=['GET'])
def osm_tags():
    return render_template('osm_tags.html')
