import json
from pathlib import Path
import re

SUGGESTIONS = None


def ensure_suggestions_loaded():
    global SUGGESTIONS
    if SUGGESTIONS is None:
        SUGGESTIONS = read_suggestions()


def read_suggestions():
    filename = (Path(__file__) / '../../data/tag_suggestions.json').resolve()
    with open(filename) as f:
        return json.load(f)


def get_suggestions(tokens):
    ensure_suggestions_loaded()
    suggestions = {}
    for token in tokens:
        suggestions_for_token = SUGGESTIONS.get(token.lower())
        if suggestions_for_token:
            suggestions[token] = suggestions_for_token
    return suggestions


def extract_suggested_tags(tag_suggestions):
    tags = set()
    for suggestions in tag_suggestions.values():
        for suggestion in suggestions:
            for match in re.finditer(r'(?P<key>[^\s=]+)=(?P<value>[^\s=]+)',
                                     suggestion):
                tags.add((match.group('key'), match.group('value')))
    return tags
