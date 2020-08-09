import re

from flask import current_app, jsonify, render_template, request

from nlmapsweb.forms.query import QueryForm
from nlmapsweb.parser import functionalise, get_geojson_features, parse
from nlmapsweb.taginfo import check_key_val_pair


def get_key_val_pairs(mrl):
    key_val_pairs = []
    for match in re.finditer(r"keyval\('(?P<key>[^']+)','(?P<val>[^']+)'\)",
                             mrl):
        key_val_pairs.append((match.group('key'), match.group('val')))
    return key_val_pairs


class ParseResult:

    def __init__(self, nl, lin, mrl, alternatives=None):
        self.nl = nl
        self.lin = lin
        self.mrl = mrl
        self.alternatives = alternatives

    @classmethod
    def from_nl(cls, nl):
        lin = parse(nl)
        mrl = functionalise(lin)

        alternatives = {}
        key_val_pairs = get_key_val_pairs(mrl)
        for key, val in key_val_pairs:
            alternatives[(key, val)] = check_key_val_pair(key, val)

        return cls(nl, lin, mrl, alternatives)

    def to_dict(self):
        return {'nl': self.nl, 'lin': self.lin, 'mrl': self.mrl}


@current_app.route('/parse', methods=['POST'])
def parse_nl():
    form = QueryForm()
    if form.validate_on_submit():
        nl = form.query.data
        result = ParseResult.from_nl(nl)
        return jsonify(result.to_dict())

    return 'Bad Request', 400


@current_app.route('/geojson', methods=['GET'])
def get_geojson():
    mrl = request.args.get('mrl')
    if mrl:
        print(mrl)
        features = get_geojson_features(mrl)
        geojson = {'type': 'FeatureCollection', 'features': features}
        return jsonify(geojson)

    return 'Bad Request!', 400


@current_app.route('/', methods=['GET'])
def query():
    form = QueryForm()
    return render_template('query.html', form=form)

