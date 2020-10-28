import difflib
import json


def get_feedback_type(systemMrl=None, correctMrl=None):
    if not systemMrl:
        return 'system-error'

    if correctMrl:
        if systemMrl == correctMrl:
            return 'correct'
        else:
            return 'incorrect'
    else:
        return 'unknown'


def get_opcodes(systemMrl, correctMrl, as_json=False):
    if get_feedback_type(systemMrl, correctMrl) == 'incorrect':
        opcodes = difflib.SequenceMatcher(
            a=systemMrl, b=correctMrl).get_opcodes()
    else:
        opcodes = None

    if as_json:
        opcodes = json.dumps(opcodes)

    return opcodes
