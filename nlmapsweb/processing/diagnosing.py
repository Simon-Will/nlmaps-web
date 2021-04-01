import itertools
from pathlib import Path
import re

from flask import current_app
import requests

from nlmaps_tools.answer_mrl import canonicalize_nwr_features

from nlmapsweb.processing.converting import mrl_to_features
from nlmapsweb.processing.custom_tag_suggestions import get_suggestions
from nlmapsweb.processing.result import Result
from nlmapsweb.processing.stop_words import is_stop_word
from nlmapsweb.processing.taginfo import (find_alternatives, taginfo_lookup,
                                          tag_is_common)
from nlmapsweb.processing.tf_idf import get_tf_idf_scores, load_tf_idf_pipeline


def get_tags_in_features(features, exclude=tuple()):
    if 'sub' in features:
        features = features['sub'][0]
    features['target_nwr'] = canonicalize_nwr_features(features['target_nwr'])

    tags = []
    for feat in features['target_nwr']:
        if feat[0] in ['or', 'and'] and isinstance(feat[1], (list, tuple)):
            for key, val in feat[1:]:
                if key not in exclude:
                    tags.append((key, val))
        elif len(feat) == 2 and all(isinstance(f, str) for f in feat):
            if feat[0] not in exclude:
                tags.append((feat[0], feat[1]))
        else:
            raise ValueError('Unexpected feature part: {}'.format(feat))

    return tags


def get_name_tokens(features):
    if features:
        if 'sub' in features:
            # For dist query features
            return list(itertools.chain.from_iterable(
                get_name_tokens(sub_features)
                for sub_features in features['sub']
            ))

        # For normal features
        tokens = []
        if 'area' in features:
            tokens.extend([
                token.lower() for token in features['area'].split()
            ])
        for feature_name in ['center_nwr', 'target_nwr']:
            for tag in features.get(feature_name, []):
                if isinstance(tag, tuple) and tag[0] == 'name':
                    tokens.extend([
                        token.lower() for token in tag[1].split()
                    ])
        return tokens

    # For empty features
    return []


class DiagnoseResult(Result):

    def __init__(self, success, nl, mrl, taginfo, tf_idf_scores,
                 custom_suggestions, error=None):
        super().__init__(success, error)
        self.nl = nl
        self.mrl = mrl
        self.taginfo = taginfo
        self.tf_idf_scores = tf_idf_scores
        self.custom_suggestions = custom_suggestions

    @classmethod
    def from_nl_mrl(cls, nl, mrl):
        success = True
        error = None
        taginfo = None
        tf_idf_scores = None
        custom_suggestions = None

        tokens = None
        features = mrl_to_features(mrl)
        if features:
            # This could just as well be a dict from the (key, val) tuple to
            # the alternatives list. But in json, we need string keys, so we
            # use a list instead of a dict.
            taginfo = []
            # Tag info for names doesn’t make sense.
            # Names are often unique.
            key_val_pairs = get_tags_in_features(features, exclude=['name'])
            try:
                counts = taginfo_lookup(key_val_pairs) or {}
                for key, val in key_val_pairs:
                    taginfo.append([
                        (key, val),
                        counts.get((key, val), 0),
                        tag_is_common(key, val),
                        find_alternatives(key, val)
                    ])
            except:
                success = False
                error = 'Failed to check key value pairs.'

            tf_idf_pipeline_file = (
                Path(__file__) / '../../data/tf_idf_pipeline.pickle'
            ).resolve()
            if tf_idf_pipeline_file:
                pipeline = load_tf_idf_pipeline(tf_idf_pipeline_file)
                if pipeline:
                    tf_idf_scores = get_tf_idf_scores(pipeline, nl)

            if tf_idf_scores:
                tokens_to_be_deleted = get_name_tokens(features)
                tokens = list(tf_idf_scores.keys())
                for token in tokens:
                    if token in tokens_to_be_deleted or is_stop_word(token):
                        del tf_idf_scores[token]

                # Singularization
                #tok_score_to_add = [
                #    (token, score) for token, score
                #    in tf_idf_scores.items() if token.endswith('s')
                #]
                #for token, score in tok_score_to_add:
                #    tf_idf_scores[token[:-1]] = score

                tokens = tf_idf_scores.keys()
        else:
            success = False
            error = 'Failed to convert mrl to features'

        if not tokens:
            tokens = nl.split(' ')
        custom_suggestions = get_suggestions(tokens)

        return cls(success=True, nl=nl, mrl=mrl, taginfo=taginfo,
                   tf_idf_scores=tf_idf_scores,
                   custom_suggestions=custom_suggestions)

    def to_dict(self):
        return {
            'nl': self.nl, 'mrl': self.mrl, 'taginfo': self.taginfo,
            'tf_idf_scores': self.tf_idf_scores,
            'custom_suggestions': self.custom_suggestions
        }
