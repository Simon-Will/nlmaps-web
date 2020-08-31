from flask import current_app, jsonify, render_template, request

from nlmapsweb.forms.query import MRLQueryForm, NLQueryForm
from nlmapsweb.parser import AnswerResult, ParseResult, get_geojson_features


@current_app.route('/parse', methods=['POST'])
def parse_nl():
    form = NLQueryForm()
    if form.validate_on_submit():
        nl = form.nl.data
        result = ParseResult.from_nl(nl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status

    return 'Bad Request', 400


@current_app.route('/answer_mrl', methods=['GET'])
def answer_mrl():
    mrl = request.args.get('mrl')
    if mrl:
        print(mrl)
        result = AnswerResult.from_mrl(mrl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status

    return 'Bad Request!', 400


@current_app.route('/', methods=['GET'])
def query():
    nl_query_form = NLQueryForm()
    mrl_query_form = MRLQueryForm()
    return render_template('query.html', mrl_query_form=mrl_query_form,
                           nl_query_form=nl_query_form)

