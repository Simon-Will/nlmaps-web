from collections import defaultdict
import difflib
import json
import os
from pathlib import Path
import re

from flask import current_app
import requests

from nlmapsweb.utils.cache import read_from_cache, write_to_cache

CACHE = 'taginfo'

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
    filename = (Path(__file__) / '../../data/most_common_tags.json').resolve()
    with open(filename) as f:
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


def make_concise(tagfinder_info):
    needed_keys = ('prefLabel', 'subject', 'isKey', 'scopeNote', 'countAll',
                   'depiction')
    return [{key: info[key] for key in needed_keys} for info in tagfinder_info]


def taginfo_lookup(key_val_pairs):

    info_by_key_val = {}
    key_val_pairs_to_look_up = []
    for key, val in key_val_pairs:
        tag = '{}={}'.format(key, val)
        info = read_from_cache(CACHE, tag)
        if info:
            info_by_key_val[(key, val)] = info
        else:
            key_val_pairs_to_look_up.append((key, val))

    url_base = current_app.config['TAGINFO_URL']
    url = url_base + 'api/4/tags/list'
    if key_val_pairs_to_look_up:
        tags_string = ','.join(
            '{}={}'.format(key, val) for key, val in key_val_pairs_to_look_up)
        current_app.logger.info('Looking up {} at url {}'.format(tags_string, url))
        response = requests.get(url, params={'tags': tags_string})
        if response.ok:
            current_app.logger.info('Lookup successful.')
            data = response.json()['data']
            for info in data:
                info = {
                    key: info[key]
                    for key in ('key', 'value', 'count_all', 'count_nodes',
                                'count_ways', 'count_relations')
                }
                key, val = info['key'], info['value']
                tag = '{}={}'.format(key, val)
                write_to_cache(CACHE, tag, info)
                info_by_key_val[(key, val)] = info
        else:
            current_app.logger.error('Lookup failed with status code {}.'
                                     .format(response.status_code))

    count_by_key_val = {}
    for key_val_pair, info in info_by_key_val.items():
        count_by_key_val[key_val_pair] = info['count_all']
    return count_by_key_val
