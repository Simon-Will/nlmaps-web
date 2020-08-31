import json
import subprocess
import traceback

from flask import current_app

from mrl import mrl
from nlmapsweb.taginfo import check_key_val_pair, get_key_val_pairs


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


def answer_query(mrl_query):
    current_app.logger.info('Interpreting query "{}".'.format(mrl_query))
    answer_cmd = current_app.config['ANSWER_COMMAND']
    try:
        proc = subprocess.run(answer_cmd, capture_output=True, input=mrl_query,
                              text=True, check=True)
    except:
        current_app.logger.warning(traceback.format_exc())
        current_app.logger.warning('Interpreting query "{}" failed.'.format(mrl_query))
        return False

    result = proc.stdout.strip()
    current_app.logger.info('Received answering result {}'.format(result))
    return result


def get_geojson_features(mrl_query):
    current_app.logger.info('Interpreting query "{}".'.format(mrl_query))
    answer_cmd = current_app.config['ANSWER_COMMAND']
    try:
        proc = subprocess.run(answer_cmd, capture_output=True, input=mrl_query,
                              text=True, check=True)
    except:
        current_app.logger.warning(traceback.format_exc())
        current_app.logger.warning('Interpreting query "{}" failed.'.format(mrl_query))
        return False

    if proc.stdout.startswith('"features": '):
        current_app.logger.info('Received result {}'.format(proc.stdout))
        features = proc.stdout[12:].strip()
        print(features, file=open('/tmp/geo.json', 'w'))
        return json.loads(features)

    current_app.logger.info('No features found.')
    return []


def functionalise(lin):
    try:
        func = mrl.MRLS['nlmaps']().functionalise(lin.strip())
    except:
        current_app.logger.warning(traceback.format_exc())
        return False

    current_app.logger.info('Functionalised "{}" to "{}"'.format(lin, func))
    return func


class Result:

    def __init__(self, success, error=None):
        self.success = success
        self.error = error


class ParseResult(Result):

    def __init__(self, success, nl, lin, mrl, error=None, alternatives=None):
        super().__init__(success, error)
        self.nl = nl
        self.lin = lin
        self.mrl = mrl
        self.alternatives = alternatives

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

        try:
            alternatives = {}
            key_val_pairs = get_key_val_pairs(mrl)
            for key, val in key_val_pairs:
                alternatives[(key, val)] = check_key_val_pair(key, val)
        except:
            error = 'Failed to check key value pairs'
            return cls(False, nl, lin, mrl, error=error)

        return cls(True, nl, lin, mrl, alternatives=alternatives)

    def to_dict(self):
        return {'nl': self.nl, 'lin': self.lin, 'mrl': self.mrl,
                'success': self.success, 'error': self.error}


class AnswerResult(Result):

    def __init__(self, success, mrl, answer, features, error=None):
        super().__init__(success, error)
        self.mrl = mrl
        self.answer = answer
        self.features = features
        self.geojson = {'type': 'FeatureCollection', 'features': features}

    @classmethod
    def from_mrl(cls, mrl):
        result = answer_query(mrl)
        if result is False:
            error = f'Failed to parse MRL query {mrl!r}'
            current_app.logger.warning(error)
            return cls(success=False, mrl=mrl, answer=None, features=[],
                       error=error)

        parts = result.strip().split('\n')
        if len(parts) != 2:
            error = f'Unexpected answering result: {result!r}'
            current_app.logger.warning(error)
            return cls(success=False, mrl=mrl, answer=None, features=[],
                       error=error)

        answer = parts[0]
        features_str = parts[1]

        if features_str.startswith('"features": '):
            features_str = features_str[12:].strip()
            try:
                features = json.loads(features_str)
            except json.JSONDecodeError:
                error = f'Error decoding the following JSON: {features_str!r}'
                current_app.logger.warning(error)
                return cls(success=False, mrl=mrl, answer=answer, features=[],
                           error=error)
        else:
            error = f'Could not find features in the string {features_str!r}'
            current_app.logger.warning(error)
            return cls(success=False, mrl=mrl, answer=answer, features=[],
                        error=error)

        return cls(success=True, mrl=mrl, answer=answer, features=features)

    def to_dict(self):
        return {'success': self.success, 'error': self.error,
                'mrl': self.mrl, 'answer': self.answer,
                'geojson': self.geojson}
