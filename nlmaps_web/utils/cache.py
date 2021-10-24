import json
import os

from flask import current_app


def get_cache_file(cache, entry):
    return os.path.join(
        current_app.config['CACHE_DIR'],
        cache,
        '{}.json'.format(entry)
    )


def read_from_cache(cache, entry):
    cache_file = get_cache_file(cache, entry)
    if os.path.isfile(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    return None


def write_to_cache(cache, entry, content):
    cache_file = get_cache_file(cache, entry)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(content, f)
