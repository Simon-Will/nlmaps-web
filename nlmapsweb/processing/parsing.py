from typing import Any, Dict, Optional

from flask import current_app

from nlmapsweb.app import db
from nlmapsweb.models import ParseLog
import nlmapsweb.mt_server as mt_server
from nlmapsweb.processing.converting import functionalise, mrl_to_features
from nlmapsweb.processing.result import Result


def parse_to_lin(nl_query: str, model: Optional[str] = None) -> Optional[str]:
    """Parse an NL into a LIN on the MT server.

    :param nl_query: NL query.
    :param model: Model used for parsing. If not given, CURRENT_MODEL from the
        config is used.
    :return: LIN query or None if parsing failed.
    """
    current_app.logger.info('Parsing query "{}".'.format(nl_query))
    model = model or current_app.config['CURRENT_MODEL']

    payload = {'model': model, 'nl': nl_query}
    response = mt_server.post('translate', json=payload)
    if response.status_code == 200:
        result = response.json()['lin']
        current_app.logger.info('Received parsing result "{}".'.format(result))
        return result

    current_app.logger.warning('Parsing failed. Response code: {}'
                               .format(response.status_code))
    return None


class ParseResult(Result):

    def __init__(self, success: bool, nl: str, lin: Optional[str],
                 mrl: Optional[str], model: str, error: Optional[str] = None):
        """Initialize the ParseResult.

        :param success: Whether the parse was successful. If true, mrl should
            also be specified. If false, error should be specified.
        :param nl: NL query issued by user.
        :param lin: LIN query returned by MT server.
        :param mrl: MRL query converted from LIN query.
        :param model: Model used for parsing.
        :param error: Error that occurred during parsing.
        """
        super().__init__(success, error)
        self.nl = nl
        self.lin = lin
        self.mrl = mrl
        self.model = model

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
    def from_nl(cls: 'ParseResult', nl: str,
                model: Optional[str] = None) -> 'ParseResult':
        """Parse an NL and return a ParseResult object.

        :param nl: NL query issued by user.
        :param model: Model used for parsing.
        :return: The resulting ParseResult holding the parsed MRL.
        """
        model = model or current_app.config['CURRENT_MODEL']
        lin = parse_to_lin(nl, model=model)
        if not lin:
            error = 'Failed to parse NL query'
            return cls(False, nl, lin, None, model=model, error=error)

        mrl = functionalise(lin)
        if not mrl:
            error = 'Parsed linear query is ungrammatical'
            current_app.logger.warning(error)

            # Try fallback model
            fallback_model = current_app.config.get('FALLBACK_MODEL')
            if fallback_model:
                current_app.logger.info(
                    'Using fallback model {}'.format(fallback_model))
                fallback_parse_result = cls.from_nl(nl, model=fallback_model)
                if fallback_parse_result.success:
                    current_app.logger.info('Fallback successful')
                    return fallback_parse_result
            # Fallback model was unsuccessful, as well.
            return cls(False, nl, lin, mrl, model=model, error=error)

        return cls(True, nl, lin, mrl, model=model)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this object into a dict.

        :return: Serialized ParseResult.
        """
        return {'nl': self.nl, 'lin': self.lin, 'mrl': self.mrl,
                'model': self.model, 'success': self.success,
                'error': self.error, 'features': self.features}
