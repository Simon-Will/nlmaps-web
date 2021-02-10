import requests

from flask import current_app


class MTServerError(Exception):
    pass


class MTServerConnectionError(MTServerError):
    pass


class MTServerConfigurationError(MTServerError):
    pass


def make_url(path, base_url=None):
    if not base_url:
        base_url = current_app.config.get('JOEY_SERVER_URL')
        if not base_url:
            raise MTServerConfigurationError('URL not in config')
    return base_url.rstrip('/') + '/' + path


def get(path, params=None, base_url=None):
    url = make_url(path, base_url=base_url)
    msg = 'GET {} with params {}. Result: {}'
    try:
        response = requests.get(url, params=params)
        current_app.logger.info(msg.format(url, params, response.status_code))
        return response
    except Exception as e:
        current_app.logger.warning(msg.format(url, params,
                                              e.__class__.__name__))
        raise MTServerConnectionError from e


def post(path, params=None, json=None, base_url=None):
    url = make_url(path, base_url=base_url)
    msg = 'POST {} to {} with params {}. Result: {}'
    try:
        response = requests.post(url, params=params, json=json)
        current_app.logger.info(msg.format(json, url, params,
                                           response.status_code))
        return response
    except Exception as e:
        current_app.logger.warning(msg.format(json, url, params,
                                              e.__class__.__name__))
        raise MTServerConnectionError from e
