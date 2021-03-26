from flask import current_app, render_template

from nlmapsweb.models import ParseLog
from nlmapsweb.utils.auth import admin_required


@current_app.route('/parse_logs', methods=['GET'])
@admin_required
def parse_logs():
    logs = ParseLog.query.all()
    return render_template('parse_logs.html', parse_logs=logs)
