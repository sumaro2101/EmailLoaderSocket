from imaplib import IMAP4

from django.conf import settings
from .abc import AbstractConnection


class GmailConnection(AbstractConnection):
    pass


class YandexConnection(AbstractConnection):
    pass


class MailConnection(AbstractConnection):
    pass
