import difflib
import json


def get_feedback_type(system_mrl=None, correct_mrl=None):
    if not system_mrl:
        return 'system-error'

    if correct_mrl:
        if system_mrl == correct_mrl:
            return 'correct'
        else:
            return 'incorrect'
    else:
        return 'unknown'


def get_opcodes(system_mrl, correct_mrl, as_json=False):
    if get_feedback_type(system_mrl, correct_mrl) == 'incorrect':
        opcodes = difflib.SequenceMatcher(
            a=system_mrl, b=correct_mrl).get_opcodes()
    else:
        opcodes = None

    if as_json:
        opcodes = json.dumps(opcodes)

    return opcodes
