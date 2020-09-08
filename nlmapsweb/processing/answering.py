import json
import subprocess
import traceback

from flask import current_app

from nlmapsweb.processing.result import Result

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
