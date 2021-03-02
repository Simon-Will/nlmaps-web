#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email.message import EmailMessage
from email.utils import formatdate, getaddresses
import itertools
import smtplib
import ssl
from typing import Sequence, Union


def EmailError(Exception):
    pass


class MySMTP:

    def __init__(self, host: str, user: str, password: str,
                 port: Union[int, str] = 0):
        self.host = host
        try:
            if isinstance(port, str):
                port = int(port)
            self.port = port

            context = ssl.create_default_context()
            self.smtp = smtplib.SMTP_SSL(host, port, context=context)
            self.smtp.login(user, password)
        except Exception as e:
            raise EmailError('Could not login at {}:{} as user {}.'
                             .format(host, port or 465, user)) from e

    def send(self, message: str, subject: str, from_: str, to: Sequence[str],
             cc: Sequence[str] = tuple(), bcc: Sequence[str] = tuple()):
        msg = EmailMessage()
        msg.set_content(message)

        msg['Subject'] = subject
        msg['From'] = from_
        msg['To'] = ','.join(to)
        if cc:
            msg['Cc'] = ','.join(cc)
        msg['Date'] = formatdate(localtime=True)

        sender, *recipients = [
            name_address_tuple[1]
            for name_address_tuple
            in getaddresses(itertools.chain([from_], to, cc, bcc))
        ]
        try:
            self.smtp.sendmail(sender, recipients, msg.as_string())
        except Exception as e:
            raise EmailError('Could not send message from {} to {}.'
                             .format(sender, ', '.join(recipients))) from e


if __name__ == '__main__':
    # Test emailing function.
    import argparse
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('host')
    PARSER.add_argument('user')
    PARSER.add_argument('password')
    PARSER.add_argument('--port', '-p', type=int, default=0)
    PARSER.add_argument('--to', '-t', default='test@example.com')
    PARSER.add_argument('--from', '-f', default='test@example.com')
    ARGS = PARSER.parse_args()

    SMTP = MySMTP(host=ARGS.host, user=ARGS.user, password=ARGS.password,
                  port=ARGS.port)
    MESSAGE = 'This message was sent to test NLMaps Web’s mailing functions.'
    SMTP.send(
        message=MESSAGE,
        subject='[NLMapsWeb] Test',
        from_=getattr(ARGS, 'from'),  # Use getattr because from is a keyword.
        to=[ARGS.to],
    )
