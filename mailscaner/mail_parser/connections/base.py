from imaplib import IMAP4
from typing import Any, Literal

from django.conf import settings
from django.forms import BaseForm

from .abc import AbstractConnection
from .exeptions import FailConnection, BaseConnectionError


class BaseConnection(AbstractConnection):
    """
    Базовое подлючение, только для элементов стратегии
    """

    __read_only = settings.EMAIL_READONLY

    def __init__(self,
                 login: str,
                 password: str,
                 mailbox: Literal['INBOX',
                                'FLAGS',
                                'EXISTS',
                                'RECENT',
                                'UIDVALIDITY',
                                ] = 'INBOX',
                 charset: str | None = None,
                 criteria: str = 'ALL',
                 ) -> None:
        self.__login = login
        self.__password = password
        self.mailbox = mailbox
        self.charset = charset
        self.criteria = criteria
        self.server: IMAP4 = None
        self.messages = None

    def _select_box(self,
                    box: str,
                    ) -> tuple[str, list[bytes | None]]:
        return self.server.select(mailbox=box,
                                  readonly=self.__read_only,
                                  )

    def _search_data(self,
                     charset: str | None,
                     criteria: str,
                     ) -> (tuple[Literal['NO'], Any] |
                          tuple[Any, list[None]] |
                          tuple):
        return self.server.search(charset, criteria)
    
    @classmethod
    def _get_imap(cls):
        raise BaseConnectionError('You need use "GmailConnection", '
                                  '"MailConnection", or "YandexConnection", '
                                  'BaseConnection is not provide')

    @classmethod
    def _get_port(cls):
        raise BaseConnectionError('You need use "GmailConnection", '
                                  '"MailConnection", or "YandexConnection", '
                                  'BaseConnection is not provide')

    @classmethod
    def connection(cls,
                   login: str,
                   password: str,
                   form: BaseForm | None = None,
                   ) -> IMAP4:
        imap = cls._get_imap()
        port = cls._get_port()
        server = IMAP4(host=imap,
                       port=port,
                       )
        try:
            server.login(login, password)
            return server
        except IMAP4.error as error:
            if not form:
                raise FailConnection(error)
            form.add_error(field=None, error=error)

    def __enter__(self) -> list[bytes]:
        return self.messages

    def action(self) -> list[bytes]:
        """
        Создание подключения с настройками
        """
        self.server = self.connection(
            login=self.__login,
            password=self.__password,
        )
        box = self._select_box(box=self.mailbox)
        self.messages = self._search_data(
            charset=self.charset,
            criteria=self.criteria,
            )[0][1]
        return self.messages