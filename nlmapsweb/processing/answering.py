import json
import subprocess
import traceback

from flask import current_app

from nlmaps_tools.answer_mrl import (
    load_features, answer as get_answer, merge_feature_collections
)

from nlmapsweb.processing.result import Result


def answer_query(mrl_query):
    current_app.logger.info('Interpreting query "{}".'.format(mrl_query))

    features = load_features(mrl_query)
    if features:
        result = get_answer(features)
        current_app.logger.info('Received py answering result')
        return result

    return {'type': 'error', 'error':  'Failed to convert mrl to features'}


class AnswerResult(Result):

    def __init__(self, success, mrl, result, error=None):
        super().__init__(success, error)
        self.mrl = mrl

        self.centers = result.pop('centers', None)
        self.targets = result.pop('targets', None)

        if 'error' in result:
            current_app.logger.error('MRL interpretation error: {}'
                                     .format(result['error']))

        self.answer = result

    @classmethod
    def from_mrl(cls, mrl):
        result = answer_query(mrl)

        if result.get('type') == 'error':
            success = False
            error = result['error']
        else:
            success = True
            error = None

        return cls(success=success, mrl=None, result=result, error=error)

    def to_dict(self):
        return {'success': self.success, 'error': self.error,
                'mrl': self.mrl, 'answer': self.answer,
                'centers': self.centers, 'targets': self.targets}
