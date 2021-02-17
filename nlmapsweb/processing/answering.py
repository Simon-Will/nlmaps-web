import json
import subprocess
import traceback

from flask import current_app

from nlmaps_tools.answer_mrl import load_features, answer

from nlmapsweb.processing.result import Result

def answer_query(mrl_query):
    current_app.logger.info('Interpreting query "{}".'.format(mrl_query))

    features = load_features(mrl_query)
    if features and features['query_type'] == 'in_query':
        result = answer(features)
        current_app.logger.info('Received py answering result {}'.format(result))
        return result


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

    def __init__(self, success, mrl, answer, features, error=None, py_result=None):
        super().__init__(success, error)
        self.mrl = mrl
        self.answer = answer
        self.features = features
        self.geojson = {'type': 'FeatureCollection', 'features': features}

        if py_result:
            if 'geojson' in py_result:
                self.geojson = py_result.pop('geojson')
                self.features = self.geojson['features']  # Do we need this?
            else:
                self.geojson = {'type': 'FeatureCollection', 'features': []}

            self.answer = json.dumps(py_result)

    @classmethod
    def from_mrl(cls, mrl):
        result = answer_query(mrl)

        if isinstance(result, dict):
            if result.get('type') == 'error':
                success = False
                error = result['error']
            else:
                success = True
                error = None
            return cls(success=success, mrl=None, answer=None, features=None,
                       error=error, py_result=result)

        if result is False:
            error = f'Failed to parse MRL query {mrl!r}'
            current_app.logger.warning(error)
            return cls(success=False, mrl=mrl, answer=None, features=[],
                       error=error)

        parts = result.strip().split('\n')
        if len(parts) != 2:
            error = f'Unexpected answering result: {result!r}'
            current_app.logger.warning(error)
            if len(parts) == 1:
                # XXX: The answer seems left out. For now, we’re trying to
                # recover by assuming an empty answer.
                parts.insert(0, 'No answer found.')
            else:
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
