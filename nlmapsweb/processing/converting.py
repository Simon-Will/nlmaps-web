import traceback

from flask import current_app

from mrl import mrl


def functionalise(lin):
    try:
        func = mrl.MRLS['nlmaps']().functionalise(lin.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return None

    current_app.logger.info('Functionalised "{}" to "{}"'.format(lin, func))
    return func
