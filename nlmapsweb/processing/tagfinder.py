from typing import Any, Dict, List, Set, Tuple

from flask import current_app
import requests

from nlmapsweb.utils.cache import read_from_cache, write_to_cache

CACHE = 'tagfinder'
TAGFINDER_URL = 'https://tagfinder.herokuapp.com/api/search'


def make_concise(tagfinder_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Discard unnecessary data from TagFinder response data."""
    needed_keys = ('prefLabel', 'subject', 'isKey', 'scopeNote', 'countAll',
                   'depiction')
    return [{key: info[key] for key in needed_keys} for info in tagfinder_info]


def get_tagfinder_info(token: str) -> List[Dict[str, Any]]:
    """Look up term in TagFinder.

    :param token: Term to look up.
    :return: Tag suggestions for the term. Most of the original data from
        TagFinder is already discarded by this time because we don’t need it.
    """
    tagfinder_info = read_from_cache(CACHE, token)
    if tagfinder_info is None:
        current_app.logger.info('Looking up {} at url {}'
                                .format(token, TAGFINDER_URL))
        response = requests.get(TAGFINDER_URL, params={'query': token})
        if not response.ok:
            current_app.logger.error('Lookup failed with status code {}.'
                                     .format(response.status_code))
            return None
        current_app.logger.info('Lookup successful.')
        tagfinder_info = make_concise(response.json())
        write_to_cache(CACHE, token, tagfinder_info)
    return tagfinder_info


def get_tagfinder_info_by_scores(
        tf_idf_scores: Dict[str, float],
        limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    """Look up terms with high TF-IDF score in TagFinder.

    The TF-IDF threshold is currently hardcoded to be 0.3

    :param tf_idf_scores: Terms and their TF-IDF scores.

    :param limit: How many tag suggestions to return for each term.

    :return: TagFinder tag suggestions for each term.
    """
    info_by_token = {}
    for token, score in tf_idf_scores.items():
        if score > 0.3:
            tagfinder_info = get_tagfinder_info(token)
            if tagfinder_info:
                info_by_token[token] = tagfinder_info[:limit]
    return info_by_token


def extract_tagfinder_tags(
        info_by_token: Dict[str, List[Dict[str, Any]]]) -> Set[Tuple[str,
                                                                     str]]:
    """Extract the tags suggested in the TagFinder info."""
    tags = set()
    for tagfinder_info in info_by_token.values():
        for info in tagfinder_info:
            if info['isKey']:
                key, val = info['prefLabel'], '*'
            else:
                key, val = info['prefLabel'].split('=')
            tags.add((key, val))
    return tags
