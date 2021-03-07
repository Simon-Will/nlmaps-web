from flask import current_app, render_template

import nlmapsweb.mt_server as mt_server
from nlmapsweb.models import User


@current_app.route('/legal_notice')
def legal_notice():
    return render_template('legal_notice.html')


@current_app.route('/terms')
def terms():
    return render_template('terms.html')


@current_app.route('/contributors')
def contributors():
    response = mt_server.post('feedback_users')
    user_ids = response.json()
    contributor_names = [
        user.contributor_name
        for user in User.query.filter(User.id.in_(user_ids))
        if user.contributor_name
    ]
    return render_template('contributors.html', names=contributor_names)
