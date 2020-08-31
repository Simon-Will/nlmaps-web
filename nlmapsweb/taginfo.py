from collections import defaultdict
import json
import re

from flask import current_app

TAGS = None

REV_TAGS = None

def read_tags():
    tags = defaultdict(set)
    with open(current_app.config['MOST_COMMON_TAGS']) as f:
        content = json.load(f)
        for entry in content['data']:
            tags[entry['key']].add(entry['value'])
    return tags


def reverse_tags(tags):
    rev_tags = defaultdict(set)
    for key, vals in tags.items():
        for val in vals:
            rev_tags[val].add(key)
    return rev_tags


def check_key_val_pair(key, val):
    global TAGS
    global REV_TAGS
    if TAGS is None:
        TAGS = read_tags()
        REV_TAGS = reverse_tags(TAGS)

    if key in TAGS:
        if val in TAGS[key]:
            return True

    alternatives = []
    # Check alternatives
    for potential_val in [val, val + 's']:
        if potential_val in REV_TAGS:
            for potential_key in REV_TAGS[potential_val]:
                alternatives.append((potential_key, potential_val))

    return alternatives


def get_key_val_pairs(mrl):
    key_val_pairs = []
    for match in re.finditer(r"keyval\('(?P<key>[^']+)','(?P<val>[^']+)'\)",
                             mrl):
        key_val_pairs.append((match.group('key'), match.group('val')))
    return key_val_pairs
