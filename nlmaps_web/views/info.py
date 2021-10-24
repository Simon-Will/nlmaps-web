from flask import current_app, render_template


@current_app.route('/datasets')
def datasets():
    available_datasets = current_app.config.get('DATASETS', [])
    return render_template('datasets.html', datasets=available_datasets)
