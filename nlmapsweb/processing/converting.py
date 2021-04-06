import json
import traceback

from flask import current_app
import pyparsing

from nlmaps_tools.mrl import NLmaps
from nlmaps_tools.generate_mrl import generate_from_features
from nlmaps_tools.parse_mrl import MrlGrammar

from nlmapsweb.models.features_cache import FeaturesCacheEntry

MRL_GRAMMAR = MrlGrammar()


def functionalise(lin):
    try:
        mrl = NLmaps().functionalise(lin.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.info('Functionalised "{}" to "{}"'.format(lin, mrl))
    return mrl


def linearise(mrl):
    try:
        # “Preprocessing” contains merging multi-word values into one
        # €-separated token. After that, it is linearised.
        lin = NLmaps().preprocess_mrl(mrl.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.info('Linearised "{}" to "{}"'.format(mrl, lin))
    return lin


def mrl_to_features(mrl, is_escaped=False):
    if not mrl:
        return None

    features = FeaturesCacheEntry.get_features_by_mrl(mrl)
    if features:
        return features

    try:
        parse_result = MRL_GRAMMAR.parseMrl(mrl, is_escaped=is_escaped)
    except pyparsing.ParseException:
        features = None
    else:
        features = parse_result['features']
        # TODO: Put this into nlmaps-tools.
        if features['query_type'] == 'dist':
            if len(features['sub']) == 1:
                features['query_type'] = 'dist_closest'
            else:
                features['query_type'] = 'dist_between'

    FeaturesCacheEntry.create(mrl, features)
    return features


def features_to_mrl(features, escape=False):
    if not features:
        return None

    # TODO: Put this into nlmaps-tools.
    if features['query_type'] in ['dist_closest', 'dist_between']:
        features['query_type'] = 'dist'

    return generate_from_features(features, escape=escape)
