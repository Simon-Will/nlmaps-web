from flask_login import current_user
from flask import current_app

from nlmaps_web.utils.smtp import MySMTP


FOOTER = (
    '\r\n'
    '---\r\n'
    'Simon Will\r\n'
    '\r\n'
    'Berliner Straße 109A\r\n'
    '69121 Heidelberg\r\n'
    'Germany\r\n'
    '\r\n'
    'nlmaps_web@nlmaps.gorgor.de\r\n'
    '\r\n'
    'https://nlmaps.gorgor.de/\r\n'
)


def send_mail(message, subject, to, cc=tuple(), bcc=tuple(), footer=FOOTER):
    if footer:
        message += footer

    if isinstance(to, str):
        to = (to,)
    if isinstance(cc, str):
        cc = (cc,)
    if isinstance(bcc, str):
        bcc = (bcc,)

    host = current_app.config.get('EMAIL_HOST')
    port = current_app.config.get('EMAIL_PORT')
    user = current_app.config.get('EMAIL_USER')
    password = current_app.config.get('EMAIL_PASSWORD')
    from_ = current_app.config.get('EMAIL_FROM')
    if host and port and user and password and from_:
        current_app.logger.info('Sending email with subject “{}” to {}.'
                                .format(subject, to))
        smtp = MySMTP(host=host, port=port, user=user, password=password)
        smtp.send(message, subject=subject, from_=from_, to=to, cc=cc, bcc=bcc)
    else:
        config = {'host': host, 'port': port, 'user': user,
                  'password': '<set>' if password else None, 'from': from_}
        current_app.logger.error('Incomplete email configuration: {}'
                                 .format(config))
