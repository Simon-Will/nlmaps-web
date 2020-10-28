from multiprocessing.pool import ThreadPool

from flask import current_app, jsonify

from nlmapsweb.app import create_app, db
from nlmapsweb.forms.parsing_model import ParsingModelForm
from nlmapsweb.models import Feedback, ParseLog
from nlmapsweb.processing.parsing import ParseResult


# TODO: This takes very long and the client has to wait without any feedback.
# It would be better to respond with a server-sent event.
@current_app.route('/batch_parse', methods=['POST'])
def batch_parse():
    form = ParsingModelForm()
    if form.validate_on_submit():
        model = form.model.data

        # Get all nls for which there is a feedback but no parse by the model
        # in question.
        nls_for_model = db.session.query(ParseLog.nl).filter(
            ParseLog.model == model)
        nls_to_parse = db.session.query(Feedback.nl).filter(
            ~Feedback.nl.in_(nls_for_model))
        nls_to_parse = [row[0] for row in nls_to_parse]

        def parse(nl):
            app = create_app()
            with app.app_context():
                return ParseResult.from_nl(nl, model=model)

        with ThreadPool(10) as pool:
            parse_results = pool.map(parse, nls_to_parse)

        status = 200 if all(res.success for res in parse_results) else 500
        return jsonify([res.to_dict() for res in parse_results]), status

    return 'Bad Request', 400
