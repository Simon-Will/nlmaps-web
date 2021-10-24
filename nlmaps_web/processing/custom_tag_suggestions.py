from typing import Dict, Iterable, Set, Tuple
import json
from pathlib import Path
import re

SUGGESTIONS = None


def ensure_suggestions_loaded() -> None:
    """Make sure the suggestions are stored in the global SUGGESTIONS."""
    global SUGGESTIONS
    if SUGGESTIONS is None:
        SUGGESTIONS = read_suggestions()


def read_suggestions() -> dict:
    """Read the suggestions from disk."""
    filename = (Path(__file__) / '../../data/tag_suggestions.json').resolve()
    with open(filename) as f:
        return json.load(f)


def get_suggestions(tokens: Iterable[str]) -> Dict[str, Dict[str, str]]:
    """Get tag suggestions for some words.

    :param tokens: The tokens for which to get suggestions.
    :return: A dict mapping a given token to another dict containing the
        suggestions. Tokens for which no suggestions exist are excluded.
    """
    ensure_suggestions_loaded()
    suggestions = {}
    for token in tokens:
        suggestions_for_token = SUGGESTIONS.get(token.lower())
        if suggestions_for_token:
            suggestions[token] = suggestions_for_token
    return suggestions


def extract_suggested_tags(
        tag_suggestions: Dict[str, Dict[str, str]]) -> Set[Tuple[str, str]]:
    """Extract the suggested tags from a nested suggestion dict.

    :param tag_suggestions: A nested suggestion dict mapping words to their
        suggestions, as returned by get_suggestions.
    :return: A set of the tags occurring in the suggestions.
    """
    tags = set()
    for suggestions in tag_suggestions.values():
        for suggestion in suggestions:
            for match in re.finditer(r'(?P<key>[^\s=]+)=(?P<value>[^\s=]+)',
                                     suggestion):
                tags.add((match.group('key'), match.group('value')))
    return tags
