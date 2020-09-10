import subprocess
import traceback

from flask import current_app

from nlmapsweb.app import db
from nlmapsweb.models import ParseLog
from nlmapsweb.processing.converting import functionalise
from nlmapsweb.processing.result import Result


def parse_to_lin(nl_query):
    current_app.logger.info('Parsing query "{}".'.format(nl_query))
    parse_cmd = current_app.config['PARSE_COMMAND']
    try:
        proc = subprocess.run(parse_cmd, capture_output=True,
                              input=nl_query, text=True, check=True)
    except:
        current_app.logger.warning(traceback.format_exc())
        current_app.logger.warning('Parsing query "{}" failed.'.format(nl_query))
        return False

    result = proc.stdout.strip()
    current_app.logger.info('Received parsing result "{}".'.format(result))
    return result


class ParseResult(Result):

    def __init__(self, success, nl, lin, mrl, error=None):
        super().__init__(success, error)
        self.nl = nl
        self.lin = lin
        self.mrl = mrl

        log = ParseLog(nl=nl, lin=lin)
        db.session.add(log)
        db.session.commit()

    @classmethod
    def from_nl(cls, nl):
        lin = parse_to_lin(nl)
        if not lin:
            error = 'Failed to parse NL query'
            return cls(False, nl, lin, None, error=error)

        mrl = functionalise(lin)
        if not mrl:
            error = 'Parsed linear query is ungrammatical'
            return cls(False, nl, lin, mrl, error=error)

        return cls(True, nl, lin, mrl)

    def to_dict(self):
        return {'nl': self.nl, 'lin': self.lin, 'mrl': self.mrl,
                'success': self.success, 'error': self.error}
