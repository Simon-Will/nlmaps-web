from typing import List, Optional, Tuple

import difflib
import json


def get_feedback_type(system_mrl: Optional[str] = None,
                      correct_mrl: Optional[str] = None) -> str:
    """Classify feedback depending on what MRLs are present."""
    if not system_mrl:
        return 'system-error'

    if correct_mrl:
        if system_mrl == correct_mrl:
            return 'correct'
        else:
            return 'incorrect'
    else:
        return 'unknown'


def get_opcodes(system_mrl: Optional[str], correct_mrl: Optional[str],
                as_json: bool = False) -> List[Tuple[str, int, int, int, int]]:
    """Get operations necessary to turn system_mrl into correct_mrl.

    This function only returns operations if both mrls are present and they
    differ from each other."""
    if get_feedback_type(system_mrl, correct_mrl) == 'incorrect':
        opcodes = difflib.SequenceMatcher(
            a=system_mrl, b=correct_mrl).get_opcodes()
    else:
        opcodes = None

    if as_json:
        opcodes = json.dumps(opcodes)

    return opcodes
