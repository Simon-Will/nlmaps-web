import os.path
import subprocess
import traceback

from flask import current_app

from nlmapsweb.app import db
from nlmapsweb.models import ParseLog
from nlmapsweb.processing.converting import functionalise, mrl_to_features
from nlmapsweb.processing.result import Result

joey_parse = None


def load_joeynmt():
    global joey_parse
    if not joey_parse:
        from nlmapsweb.processing.joeynmt_wrapper import joey_parse


def parse_to_lin_by_cmd(nl_query, cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True,
                              input=nl_query, text=True, check=True)
    except:
        current_app.logger.warning(traceback.format_exc())
        current_app.logger.warning('Parsing query "{}" failed.'.format(nl_query))
        return False

    result = proc.stdout.strip()
    return result


def parse_to_lin(nl_query, model=None):
    current_app.logger.info('Parsing query "{}".'.format(nl_query))
    model = model or current_app.config['CURRENT_MODEL']
    model_action = current_app.config['MODELS'].get(model)
    if isinstance(model_action, list):
        # It is an argument list, i.e. a parse command.
        result = parse_to_lin_by_cmd(nl_query, model_action)
    elif os.path.isfile(model_action):
        # It is a config path, i.e. enables local joeynmt execution.
        load_joeynmt()
        result = joey_parse(nl_query, model_action)
    elif model_action is None:
        current_app.logger.warning('Could not find {} in MODELS'.format(model))
    else:
        current_app.logger.warning('Model action {} was not understood'
                                   .format(model_action))

    if result:
        current_app.logger.info('Received parsing result "{}".'.format(result))

    return result


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
