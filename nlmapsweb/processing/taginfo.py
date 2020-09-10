from collections import defaultdict
import difflib
import json
import re

from flask import current_app

TAGS = None

REV_TAGS = None

def ensure_tags_loaded():
    global TAGS
    global REV_TAGS
    if TAGS is None:
        TAGS = read_tags()
        REV_TAGS = reverse_tags(TAGS)

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


def get_tags_with_similar_vals(val):
    ensure_tags_loaded()
    tags = []
    similar_vals = difflib.get_close_matches(val, REV_TAGS.keys(), n=5,
                                             cutoff=0.8)
    for suggested_val in similar_vals:
        for suggested_key in REV_TAGS[suggested_val]:
            tags.append((suggested_key, suggested_val))

    return tags


def find_alternatives(val):
    alternatives = get_tags_with_similar_vals(val)
    val_parts = val.split('_')
    if len(val_parts) > 1:
        for part in val_parts:
            alternatives.extend(get_tags_with_similar_vals(part))

    return alternatives


def tag_is_common(key, val):
    ensure_tags_loaded()
    return key in TAGS and val in TAGS[key]


def get_key_val_pairs(mrl):
    key_val_pairs = []
    for match in re.finditer(r"keyval\('(?P<key>[^']+)','(?P<val>[^']+)'\)",
                             mrl):
        key_val_pairs.append((match.group('key'), match.group('val')))
    return key_val_pairs
