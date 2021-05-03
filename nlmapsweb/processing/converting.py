import traceback
from typing import Any, Dict, Optional

from flask import current_app
import pyparsing

from nlmaps_tools.mrl import NLmaps
from nlmaps_tools.generate_mrl import generate_from_features
from nlmaps_tools.parse_mrl import MrlGrammar

from nlmapsweb.models.features_cache import FeaturesCacheEntry

MRL_GRAMMAR = MrlGrammar()


def functionalise(lin: str) -> Optional[str]:
    """Convert a LIN into an MRL.

    Can fail if LIN is ungrammatical.

    :param lin: The LIN.
    :return: The MRL if successful, else None.
    """
    try:
        mrl = NLmaps().functionalise(lin.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.debug('Functionalised "{}" to "{}"'.format(lin, mrl))
    return mrl


def linearise(mrl: str) -> Optional[str]:
    """Convert an MRL into a LIN.

    Can fail if MRL is ungrammatical.

    :param mrl: The MRL.
    :return: The LIN if successful, else None.
    """
    try:
        # “Preprocessing” contains merging multi-word values into one
        # €-separated token. After that, it is linearised.
        lin = NLmaps().preprocess_mrl(mrl.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.debug('Linearised "{}" to "{}"'.format(mrl, lin))
    return lin


def mrl_to_features(mrl: str, is_escaped: bool = False) -> Dict[str, Any]:
    """Parse MRL and extract its features.

    Can fail if MRL is ungrammatical.

    :param mrl: The MRL.
    :param is_escaped: Whether quotes and backslashes in quoted values are
        escaped. This should always be False for now.
    :return: The features dict if successful, else None.
    """
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


def features_to_mrl(features: dict, escape: bool = False) -> str:
    """Generate a MRL from the given features.

    Can fail if there are some infos missing in the features.

    :param features: The given MRL features.
    :param escape: Whether to escape quotes and backslashes in quoted values.
        This should always be False for now.
    :return: The generated MRL if successful, else None
    """
    if not features:
        return None

    # TODO: Put this into nlmaps-tools.
    if features['query_type'] in ['dist_closest', 'dist_between']:
        features['query_type'] = 'dist'

    return generate_from_features(features, escape=escape)
