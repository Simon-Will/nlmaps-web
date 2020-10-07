from collections import Counter, OrderedDict

from flask import current_app, render_template

from nlmapsweb.models import Feedback


@current_app.route('/tags', methods=['GET'])
def tags():
    tag_tokens = [tag for piece in Feedback.query.all() for tag in piece.tags]
    tag_counts = OrderedDict(sorted(
        Counter(tag_tokens).items(),
        key=lambda pair: pair[1],
        reverse=True
    ))
    return render_template('tags.html', tag_counts=tag_counts)
