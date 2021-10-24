from typing import Any, Dict, Optional

from flask import current_app

from nlmaps_tools.answer_mrl import (
    load_features, answer as get_answer, merge_feature_collections
)

from nlmaps_web.processing.result import Result


def answer_query(mrl: str) -> Dict[str, Any]:
    """Interpret an MRL, query Overpass and return an answer.

    See the nlmaps-tools package for what the answer will look like.

    :param The MRL.
    :return: The answer dict with answer or an error message.
    """
    current_app.logger.info('Interpreting query "{}".'.format(mrl))

    features = load_features(mrl)
    if features:
        result = get_answer(features)
        current_app.logger.info('Received py answering result')
        return result

    return {'type': 'error', 'error':  'Failed to convert mrl to features'}


class AnswerResult(Result):

    def __init__(self, mrl: str, answer: Dict[str, Any]):
        """Initialize an AnswerResult.

        :param success: Whether the MRL was successfully answered. If False, an
            error message should be given.

        :param mrl: The MRL that was answered.
        :param answer: The answer as given by the nlmaps_tools.answer_mrl
            module.
        :param error: Error that occurred during answering.
        """
        if answer.get('type') == 'error':
            success = False
            error = answer.get('error', 'Unknown error')
            current_app.logger.error('MRL interpretation error: {}'
                                     .format(error))
        else:
            success = True
            error = None

        super().__init__(success, error)

        self.mrl = mrl

        self.centers = answer.pop('centers', None)
        self.targets = answer.pop('targets', None)
        self.answer = answer

    @classmethod
    def from_mrl(cls: 'AnswerResult', mrl: str) -> 'AnswerResult':
        """Interpret an MRL and return an AnswerResult object"""
        answer = answer_query(mrl)
        return cls(mrl=mrl, answer=answer)

    def to_dict(self):
        """Serialize this object into a dict.

        :return: Serialized ParseResult.
        """
        return {'success': self.success, 'error': self.error,
                'mrl': self.mrl, 'answer': self.answer,
                'centers': self.centers, 'targets': self.targets}
