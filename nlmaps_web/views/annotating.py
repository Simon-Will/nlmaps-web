from collections import defaultdict, namedtuple

from flask_login import current_user, login_required
from flask import current_app, render_template

import nlmaps_web.mt_server as mt_server
from nlmaps_web.processing.converting import mrl_to_features, functionalise
from nlmaps_web.processing.diagnosing import get_tags_in_features

Progress = namedtuple('Progress', ['achieved', 'expected', 'percentage'])


def get_progress(achieved, expected):
    if achieved > expected:
        percentage = 100
    else:
        percentage = round((achieved / expected) * 100)
    return Progress(achieved, expected, percentage)


@current_app.route('/annotation_progress', methods=['GET'])
@login_required
def annotation_progress():
    filters = {'user_id': current_user.id}
    response = mt_server.post('list_feedback', json=filters)
    lins = [piece['correct_lin'] for piece in response.json()
            if not piece.get('parent_id')]
    total_feedback = len(lins)
    mrls = [mrl for mrl
            in (functionalise(lin) for lin in lins if lin)
            if mrl]
    all_features = []
    for mrl in mrls:
        features = mrl_to_features(mrl)
        if features:
            all_features.append(features)

    quests = current_app.config.get('QUESTS', {})
    quests.setdefault('total', 0)
    quests.setdefault('tags', {})
    quests.setdefault('keys', {})
    quests.setdefault('key_prefixes', {})

    total_complete = len(all_features)
    total_incomplete = (total_feedback - total_complete)
    total_annotations = total_complete + round(total_incomplete / 4)

    achieved = {
        'total': total_annotations,
        'tags': defaultdict(lambda: 0),
        'keys': defaultdict(lambda: 0),
        'key_prefixes': defaultdict(lambda: 0),
    }

    for features in all_features:
        tags = set(get_tags_in_features(features))
        for tag in tags:
            achieved['tags'][tag] += 1

        keys = {tag[0] for tag in tags}
        for key in keys:
            achieved['keys'][key] += 1
            for key_prefix in quests['key_prefixes']:
                if key.startswith(key_prefix):
                    achieved['key_prefixes'][key_prefix] += 1

    quest_progress = {
        'total': get_progress(achieved['total'], quests['total']),
        'tags': {}, 'keys': {}, 'key_prefixes': {},
        'total_complete': total_complete,
        'total_incomplete': total_incomplete,
    }
    for quest_type in ('tags', 'keys', 'key_prefixes'):
        for quest in quests[quest_type]:
            quest_progress[quest_type][quest] = get_progress(
                achieved[quest_type][quest], quests[quest_type][quest])

    return render_template('annotation_progress.html',
                           quest_progress=quest_progress)
