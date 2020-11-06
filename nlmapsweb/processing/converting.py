import traceback

from flask import current_app
import pyparsing

from mrl import NLmaps
from nlmaps_tools.parse_mrl import MrlGrammar

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


def delete_spaces(mrl):
    return NLmaps().delete_spaces(mrl)


def mrl_to_features(mrl, is_escaped=False):
    try:
        parse_result = MRL_GRAMMAR.parseMrl(mrl, is_escaped=is_escaped)
    except pyparsing.ParseException:
        features = None
    else:
        features = parse_result['features']
    return features
