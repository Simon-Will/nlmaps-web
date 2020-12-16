from flask import current_app
import requests

from nlmapsweb.app import db
from nlmapsweb.models import ParseLog
from nlmapsweb.processing.converting import functionalise, mrl_to_features
from nlmapsweb.processing.result import Result


def parse_to_lin(nl_query, model=None):
    current_app.logger.info('Parsing query "{}".'.format(nl_query))
    model = model or current_app.config['CURRENT_MODEL']
    config_file = current_app.config['MODELS'].get(model)
    if not config_file:
        current_app.logger.warning('Model not found: {}'.format(model))

    url = current_app.config['JOEY_SERVER_URL']
    payload = {'model': config_file, 'nl': nl_query}

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()['lin']
        current_app.logger.info('Received parsing result "{}".'.format(result))
        return result

    current_app.logger.warning('Parsing failed. Response code: {}'
                               .format(response.status_code))


class ParseResult(Result):

    def __init__(self, success, nl, lin, mrl, model, error=None):
        super().__init__(success, error)
        self.nl = nl
        self.lin = lin
        self.mrl = mrl

        log = ParseLog(nl=nl, lin=lin, mrl=mrl, model=model)
        db.session.add(log)
        db.session.commit()

        self.features = None
        if self.mrl:
            features = mrl_to_features(mrl, is_escaped=False)
            if features:
                self.features = features
            else:
                current_app.logger.warning(
                    'MrlGrammar could not parse mrl {!r}'.format(self.mrl)
                )

    @classmethod
    def from_nl(cls, nl, model=None):
        model = model or current_app.config['CURRENT_MODEL']
        lin = parse_to_lin(nl, model=model)
        if not lin:
            error = 'Failed to parse NL query'
            return cls(False, nl, lin, None, model=model, error=error)

        mrl = functionalise(lin)
        if not mrl:
            error = 'Parsed linear query is ungrammatical'
            return cls(False, nl, lin, mrl, model=model, error=error)

        return cls(True, nl, lin, mrl, model=model)

    def to_dict(self):
        return {'nl': self.nl, 'lin': self.lin, 'mrl': self.mrl,
                'success': self.success, 'error': self.error,
                'features': self.features}
