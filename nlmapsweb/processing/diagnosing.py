from pathlib import Path
import re

from flask import current_app
import requests

from nlmapsweb.processing.converting import mrl_to_features
from nlmapsweb.processing.result import Result
from nlmapsweb.processing.stop_words import is_stop_word
from nlmapsweb.processing.taginfo import (find_alternatives, get_key_val_pairs,
                                          taginfo_lookup, tag_is_common)
from nlmapsweb.processing.tf_idf import get_tf_idf_scores, load_tf_idf_pipeline


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

    def __init__(self, success, nl, mrl, taginfo, area, tf_idf_scores,
                 error=None):
        super().__init__(success, error)
        self.nl = nl
        self.mrl = mrl
        self.taginfo = taginfo
        self.area = area
        self.tf_idf_scores = tf_idf_scores

    @classmethod
    def from_nl_mrl(cls, nl, mrl):
        success = True
        error = None
        taginfo = None
        tf_idf_scores = None

        try:
            # This could just as well be a dict from the (key, val) tuple to
            # the alternatives list. But in json, we need string keys, so we
            # use a list instead of a dict.
            taginfo = []
            # Tag info for names doesn’t make sense.
            # Names are often unique.
            key_val_pairs = [(key, val) for key, val in get_key_val_pairs(mrl)
                             if key != 'name']
            counts = taginfo_lookup(key_val_pairs) or {}
            for key, val in key_val_pairs:
                taginfo.append([
                    (key, val),
                    counts.get((key, val), 0),
                    tag_is_common(key, val),
                    find_alternatives(val)
                ])
        except:
            success = False
            error = 'Failed to check key value pairs.'
            #return cls(success=False, nl=nl, mrl=mrl, taginfo={},
            #           area=None, tf_idf_scores=None, error=error)


        tf_idf_pipeline_file = (
            Path(__file__) / '../../data/tf_idf_pipeline.pickle'
        ).resolve()
        if tf_idf_pipeline_file:
            pipeline = load_tf_idf_pipeline(tf_idf_pipeline_file)
            if pipeline:
                tf_idf_scores = get_tf_idf_scores(pipeline, nl)

        if tf_idf_scores:
            features = mrl_to_features(mrl)
            tokens_to_be_deleted = []
            if features:
                if 'area' in features:
                    tokens_to_be_deleted.extend([
                        token.lower() for token in features['area'].split()
                    ])
                if 'center_nwr' in features:
                    for tag in features['center_nwr']:
                        if isinstance(tag, tuple) and tag[0] == 'name':
                            tokens_to_be_deleted.extend([
                                token.lower() for token in tag[1].split()
                            ])
            tokens = list(tf_idf_scores.keys())
            for token in tokens:
                if token in tokens_to_be_deleted or is_stop_word(token):
                    del tf_idf_scores[token]

        area_name = get_area_name(mrl)
        if area_name:
            area_count = count_areas(area_name)
            area = {'name': area_name, 'count': area_count}
        else:
            area = None

        return cls(success=True, nl=nl, mrl=mrl, taginfo=taginfo,
                   area=area, tf_idf_scores=tf_idf_scores)

    def to_dict(self):
        return {'nl': self.nl, 'mrl': self.mrl,
                'taginfo': self.taginfo, 'area': self.area,
                'tf_idf_scores': self.tf_idf_scores}
