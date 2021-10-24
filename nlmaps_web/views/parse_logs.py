from flask import current_app, render_template

from nlmaps_web.models import ParseLog
from nlmaps_web.utils.auth import admin_required


@current_app.route('/parse_logs', methods=['GET'])
@admin_required
def parse_logs():
    logs = ParseLog.query.all()
    return render_template('parse_logs.html', parse_logs=logs)
