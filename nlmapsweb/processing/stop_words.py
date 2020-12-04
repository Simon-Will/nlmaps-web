from flask import current_app

STOP_WORDS = None


def ensure_stop_words_loaded():
    global STOP_WORDS
    if STOP_WORDS is None:
        try:
            with open(current_app.config['STOP_WORDS']) as f:
                STOP_WORDS = {word.strip() for word in f}
        except:
            current_app.warning('Error while reading stop words file.')
            STOP_WORDS = []


def is_stop_word(word):
    ensure_stop_words_loaded()
    return word in STOP_WORDS
