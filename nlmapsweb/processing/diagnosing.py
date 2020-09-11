import re

from flask import current_app
import requests

from nlmapsweb.processing.result import Result
from nlmapsweb.processing.taginfo import (find_alternatives, get_key_val_pairs,
                                          tag_is_common)


def get_area_name(mrl):
    match = re.search(r"area\(keyval\('name','(?P<name>[^']+)'", mrl)
    if match:
        return match.group('name')


def count_areas(name):
    overpass_url = current_app.config.get('OVERPASS_URL')
    query = '[out:json];area[name="{}"];out ids;'.format(name)
    result = requests.get(overpass_url, params={'data': query})
    if result.status_code == 200:
        return len(result.json()['elements'])


class DiagnoseResult(Result):

    def __init__(self, success, nl, mrl, alternatives, area, error=None):
        super().__init__(success, error)
        self.nl = nl
        self.mrl = mrl
        self.alternatives = alternatives
        self.area = area

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
            return cls(False, nl, mrl, {}, None, error=error)

        area_name = get_area_name(mrl)
        if area_name:
            area_count = count_areas(area_name)
            area = {'name': area_name, 'count': area_count}
        else:
            area = None

        return cls(True, nl, mrl, alternatives, area)

    def to_dict(self):
        return {'nl': self.nl, 'mrl': self.mrl,
                'alternatives': self.alternatives, 'area': self.area}
