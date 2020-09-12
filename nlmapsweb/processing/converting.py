import traceback

from flask import current_app

from mrl import NLmaps


def functionalise(lin):
    try:
        func = NLmaps().functionalise(lin.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.info('Functionalised "{}" to "{}"'.format(lin, func))
    return func


def delete_spaces(mrl):
    return NLmaps().delete_spaces(mrl)
