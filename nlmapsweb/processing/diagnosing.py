from nlmapsweb.processing.result import Result
from nlmapsweb.processing.taginfo import (find_alternatives, get_key_val_pairs,
                                          tag_is_common)


class DiagnoseResult(Result):

    def __init__(self, success, nl, mrl, alternatives, error=None):
        super().__init__(success, error)
        self.nl = nl
        self.mrl = mrl
        self.alternatives = alternatives

    @classmethod
    def from_nl_mrl(cls, nl, mrl):
        try:
            # This could just as well be a dict from the (key, val) tuple to
            # the alternatives list. But in json, we need string keys, so we
            # use a list instead of a dict.
            alternatives = []
            key_val_pairs = get_key_val_pairs(mrl)
            for key, val in key_val_pairs:
                # Tag info for names doesn’t make sense.
                # They are often unique.
                if key != 'name':
                    alternatives.append(
                        ((key, val), tag_is_common(key, val),
                         find_alternatives(val))
                    )
        except:
            error = 'Failed to check key value pairs.'
            return cls(False, nl, mrl, {}, error=error)

        return cls(True, nl, mrl, alternatives)

    def to_dict(self):
        return {'nl': self.nl, 'mrl': self.mrl,
                'alternatives': self.alternatives}
