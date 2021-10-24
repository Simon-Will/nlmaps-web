from flask import current_app, jsonify, render_template, request, session

from nlmaps_web.app import db
from nlmaps_web.forms import (DiagnoseForm, QueryFeaturesForm, MrlQueryForm,
                             NlQueryForm)
from nlmaps_web.processing.answering import AnswerResult
from nlmaps_web.processing.diagnosing import DiagnoseResult
from nlmaps_web.processing.converting import features_to_mrl, mrl_to_features
from nlmaps_web.processing.parsing import ParseResult
from nlmaps_web.tutorial import tutorial_dummy_parser


@current_app.route('/', methods=['GET'])
def query():
    """Serve the main page"""
    nl_query_form = NlQueryForm()
    mrl_query_form = MrlQueryForm()
    query_features_form = QueryFeaturesForm()
    return render_template(
        'query.html', mrl_query_form=mrl_query_form,
        nl_query_form=nl_query_form,
        query_features_form=query_features_form,
    )


@current_app.route('/parse', methods=['POST'])
def parse_nl():
    """Parse NL query into a ParseResult including the MRL.

    Use by Ajax.
    """
    form = NlQueryForm()
    if form.validate_on_submit():
        nl = form.nl.data.strip()
        result = tutorial_dummy_parser(nl)
        if not result:
            result = ParseResult.from_nl(nl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status
    return 'Bad Request', 400


@current_app.route('/mrl_to_features', methods=['POST'])
def mrl_to_features_view():
    """Parse MRL into MRL features.

    Use by Ajax.
    """
    form = MrlQueryForm()
    if form.validate_on_submit():
        mrl = form.mrl.data.strip()
        features = mrl_to_features(mrl)
        if features:
            return jsonify(features), 200
    return 'Bad Request', 400


@current_app.route('/features_to_mrl', methods=['POST'])
def features_to_mrl_view():
    """Generate MRL from MRL features.

    Use by Ajax.
    """
    form = QueryFeaturesForm()
    print(request.form)
    if form.validate_on_submit():
        print(form.data)
        features = form.get_features()
        mrl = features_to_mrl(features)
        if mrl:
            return mrl, 200
    if form.errors:
        return jsonify({'errors': form.formatted_errors}), 400
    return 'Bad Request', 400


@current_app.route('/answer_mrl', methods=['GET'])
def answer_mrl():
    """Interpret an MRL and return AnswerResult including GeoJSON
    and answer dict.

    Use by Ajax.
    """
    mrl = request.args.get('mrl')
    if mrl:
        mrl = mrl.strip()
        result = AnswerResult.from_mrl(mrl)
        status = 200 if result.success else 500

        return jsonify(result.to_dict()), status
    return 'Bad Request', 400


@current_app.route('/diagnose', methods=['POST'])
def diagnose():
    """Diagnose potential problems in NL-MRL combination.

    Use by Ajax.
    """
    form = DiagnoseForm()
    if form.validate_on_submit():
        nl = form.nl.data
        mrl = form.mrl.data.strip()
        result = DiagnoseResult.from_nl_mrl(nl, mrl)
        status = 200 if result.success else 500
        return jsonify(result.to_dict()), status
    return 'Bad Request', 401
