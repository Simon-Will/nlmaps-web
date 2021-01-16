from flask import current_app, jsonify, render_template, request

from nlmapsweb.app import db
from nlmapsweb.forms import (DiagnoseForm, QueryFeaturesForm, MrlQueryForm,
                             NlQueryForm)
from nlmapsweb.processing.answering import AnswerResult
from nlmapsweb.processing.diagnosing import DiagnoseResult
from nlmapsweb.processing.converting import (delete_spaces, features_to_mrl,
                                             mrl_to_features)
from nlmapsweb.processing.parsing import ParseResult


@current_app.route('/mrl_to_features', methods=['POST'])
def mrl_to_features_view():
    form = MrlQueryForm()
    if form.validate_on_submit():
        mrl = delete_spaces(form.mrl.data.strip())
        features = mrl_to_features(mrl)
        if features:
            return jsonify(features), 200
    return 'Bad Request', 400


@current_app.route('/features_to_mrl', methods=['POST'])
def features_to_mrl_view():
    form = QueryFeaturesForm()
    print(request.form)
    if form.validate_on_submit():
        print(form.data)
        features = form.get_features()
        mrl = features_to_mrl(features)
        if mrl:
            return mrl, 200
    if form.validate():
        print('VALID')
    else:
        print('INVALID')
    print(form.errors)
    if form.errors:
        return jsonify(form.errors), 400
    return 'Bad Request', 400


@current_app.route('/parse', methods=['POST'])
def parse_nl():
    form = NlQueryForm()
    if form.validate_on_submit():
        nl = form.nl.data.strip()
        result = ParseResult.from_nl(nl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status

    return 'Bad Request', 400


@current_app.route('/answer_mrl', methods=['GET'])
def answer_mrl():
    mrl = request.args.get('mrl')
    if mrl:
        mrl = delete_spaces(mrl)
        result = AnswerResult.from_mrl(mrl)
        status = 200 if result.success else 500

        return jsonify(result.to_dict()), status

    return 'Bad Request', 400


@current_app.route('/', methods=['GET'])
def query():
    nl_query_form = NlQueryForm()
    mrl_query_form = MrlQueryForm()
    query_features_form = QueryFeaturesForm()
    return render_template(
        'query.html', mrl_query_form=mrl_query_form,
        nl_query_form=nl_query_form,
        query_features_form=query_features_form,

    )


@current_app.route('/diagnose', methods=['POST'])
def diagnose():
    form = DiagnoseForm()
    if form.validate_on_submit():
        nl = form.nl.data
        mrl = form.mrl.data
        mrl = delete_spaces(mrl)
        result = DiagnoseResult.from_nl_mrl(nl, mrl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status

    return 'Bad Request', 401
