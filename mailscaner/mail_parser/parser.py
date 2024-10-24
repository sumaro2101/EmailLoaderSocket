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
    __decode = settings.DECODER

    def __init__(self,
                 connection: 'GmailConnection' |
                 'YandexConnection' |
                 'MailConnection',
                 ) -> None:
        self.messages = connection
        self.server = connection.server

    def load_messages(self):
        leng = len(self.messages) - 1
        if self.from_end_to_start:
            while leng != -1:
                pass
        else:
            for index, message in enumerate(self.messages):
                pass