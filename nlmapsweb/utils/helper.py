from collections import defaultdict
import datetime as dt
import random
import string


def get_utc_now(aware=True):
    if aware:
        return dt.datetime.now(dt.timezone.utc)
    else:
        return dt.datetime.utcnow()


def sort_nwr(nwr_features):
    parts = []
    for feat in nwr_features:
        if feat[0] == 'or' and isinstance(feat[1], (tuple, list)):
            key_to_vals = defaultdict(set)
            for subfeat in feat[1:]:
                if isinstance(subfeat[1], (tuple, list)):
                    vals = set(subfeat[1][1:])
                else:
                    vals = {subfeat[1]}
                key_to_vals[subfeat[0]].update(vals)
            subparts = []
            for key, vals in key_to_vals.items():
                if len(vals) == 1:
                    subparts.append([key, vals.pop()])
                else:
                    subparts.append([key, ['or', *sorted(vals)]])
            if len(subparts) == 1:
                parts.append(subparts[0])
            else:
                parts.append(['or', *sorted(subparts)])

        elif feat[0] == 'and' and isinstance(feat[1], (tuple, list)):
            parts.append(['and', *sort_nwr(feat[1:])])

        elif (len(feat) == 2 and isinstance(feat[1], (tuple, list))
              and feat[1][0] == 'or'):
            parts.append([feat[0], ['or', *sorted(feat[1][1:])]])

        elif len(feat) == 2 and all(isinstance(elm, str) for elm in feat):
            parts.append([feat[0], feat[1]])

        else:
            raise ValueError('Unexpected nwr_features feat: {}'.format(feat))

    return sorted(parts)


def random_string_with_digits(length: int = 8) -> str:
    """
    Generate a random string of letters and digits
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
