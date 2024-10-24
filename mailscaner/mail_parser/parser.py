from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from .connections import GmailConnection
    from .connections import YandexConnection
    from .connections import MailConnection


class ParserMessages:
    """
    Парсер сообщений
    """
    from_end_to_start = True
    __RFC = settings.RFC822

    def __init__(self,
                 connection: 'GmailConnection' |
                 'YandexConnection' |
                 'MailConnection',
                 ) -> None:
        self.messages = connection.messages
        self.server = connection.server

    