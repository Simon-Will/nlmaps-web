from flask import current_app, jsonify, render_template, request

from nlmapsweb.app import db
from nlmapsweb.forms import FeedbackForm, MrlQueryForm, NlQueryForm
from nlmapsweb.models import Feedback
from nlmapsweb.processing import AnswerResult, ParseResult


@current_app.route('/parse', methods=['POST'])
def parse_nl():
    form = NlQueryForm()
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
    nl_query_form = NlQueryForm()
    mrl_query_form = MrlQueryForm()
    return render_template('query.html', mrl_query_form=mrl_query_form,
                           nl_query_form=nl_query_form)


@current_app.route('/feedback', methods=['POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        data = form.get_data(exclude=['csrf_token'])
        print(data)
        fb = Feedback(**data)
        db.session.add(fb)
        db.session.commit()
        return 'OK', 200
    else:
        print(form.errors)
    return 'Bad Request!', 400
