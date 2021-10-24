from pathlib import Path

from flask import current_app

STOP_WORDS = None


def ensure_stop_words_loaded():
    global STOP_WORDS
    if STOP_WORDS is None:
        try:
            filename = (Path(__file__) / '../../data/stop_words.txt').resolve()
            with open(filename) as f:
                STOP_WORDS = {word.strip() for word in f}
        except:
            current_app.warning('Error while reading stop words file.')
            STOP_WORDS = []


def is_stop_word(word):
    ensure_stop_words_loaded()
    return word in STOP_WORDS
