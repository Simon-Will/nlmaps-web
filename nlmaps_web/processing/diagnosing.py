import itertools
from pathlib import Path
from typing import Any, Container, Dict, List, Optional, Tuple

from flask import current_app

from nlmaps_tools.answer_mrl import canonicalize_nwr_features

from nlmaps_web.processing.converting import mrl_to_features
from nlmaps_web.processing.custom_tag_suggestions import get_suggestions
from nlmaps_web.processing.result import Result
from nlmaps_web.processing.stop_words import is_stop_word
from nlmaps_web.processing.taginfo import (find_alternatives, taginfo_lookup,
                                          tag_is_common)
from nlmaps_web.processing.tf_idf import get_tf_idf_scores, load_tf_idf_pipeline


def get_tags_in_features(
        features: Dict[str, Any],
        exclude: Container[str] = tuple()) -> List[Tuple[str, str]]:
    """Get all tags that occur in features.

    :param features: MRL features.
    :param exclude: Keys that should be skipped when extracting the tags. E.g.
        supply ['name'] to skip the name=* tags.
    :return: Tags occurring in features.
    """
    # TODO: Why does this function not care about center_nwr? Maybe a bug?

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


def get_name_tokens(features: Dict[str, Any]) -> List[str]:
    """Get named entities from features.

    This function extracts the value of the area field and all values of any
    name=* tags.

    :param features: MRL features.
    :return: The named entities.
    """
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

    def __init__(self, success: bool, nl: str, mrl: str,
                 taginfo: Optional[List[Tuple]],
                 tf_idf_scores: Dict[str, float],
                 custom_suggestions: Dict[str, Dict[str, str]], error=None):
        """Initialize the DiagnoseResult.

        :param success: Whether diagnosing was successful. If false, error
            should be specified.
        :param nl: NL query issued by user.
        :param mrl: Corresponding MRL query.
        :param taginfo: Information about the frequency of the used tags and
            similarly spelled tags.
        :param tf_idf_scores: TF IDF scores for the tokens in the NL. The
            higher the score, the more surprising/key it is for the query.
        :param custom_suggestions: Custom tag suggestions based on the tokens
            in the query.
        :param error: Error that occurred during parsing.
        """
        super().__init__(success, error)
        self.nl = nl
        self.mrl = mrl
        self.taginfo = taginfo
        self.tf_idf_scores = tf_idf_scores
        self.custom_suggestions = custom_suggestions

    @classmethod
    def from_nl_mrl(cls: 'DiagnoseResult', nl: str,
                    mrl: str) ->  'DiagnoseResult':
        """Diagnose a NL-MRL mapping and return a DiagnoseResult.

        :param nl: NL query issued by user.
        :param mrl: Corresponding MRL query.
        :return: The resulting DiagnoseResult holding help for judging and
            improving the MRL.
        """
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
            # Tag info for names doesn???t make sense because names are usually
            # unique (or nearly so.)
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

                # Very naive singularization.
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

        return cls(success=success, error=error, nl=nl, mrl=mrl,
                   taginfo=taginfo, tf_idf_scores=tf_idf_scores,
                   custom_suggestions=custom_suggestions)

    def to_dict(self):
        """Serialize this object into a dict.

        :return: Serialized DiagnoseResult.
        """
        return {
            'nl': self.nl, 'mrl': self.mrl, 'taginfo': self.taginfo,
            'tf_idf_scores': self.tf_idf_scores,
            'custom_suggestions': self.custom_suggestions,
            'error': self.error
        }
