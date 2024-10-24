from django.conf import settings

from .base import BaseConnection


class GmailConnection(BaseConnection):
    """
    Gmail.com соединение
    """

    @classmethod
    def _get_imap(cls):
        return settings.IMAP_GMAIL

    @classmethod
    def _get_port(cls):
        return settings.PORT_GMAIL


class YandexConnection(BaseConnection):
    """
    Yandex.ru соединение
    """

    @classmethod
    def _get_imap(cls):
        return settings.IMAP_YANDEX

    @classmethod
    def _get_port(cls):
        return settings.PORT_YANDEX


class MailConnection(BaseConnection):
    """
    Mail.ru соединение
    """

    @classmethod
    def _get_imap(cls):
        return settings.IMAP_MAIL

    @classmethod
    def _get_port(cls):
        return settings.PORT_MAIL
