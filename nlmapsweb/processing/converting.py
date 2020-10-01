import traceback

from flask import current_app

from mrl import NLmaps


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
