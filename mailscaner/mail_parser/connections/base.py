from imaplib import IMAP4_SSL, IMAP4
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
        self.server: IMAP4_SSL = None
        self.messages = self.action()

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
                   ) -> IMAP4_SSL:
        """
        Соединение с сервером

        Args:
            login (str): Email или login
            password (str): Пароль
            form (BaseForm | None, optional): В случае проверки подлинности
            Эмеила.

        Returns:
            IMAP4: IMAP сервер
        """        
        imap = cls._get_imap()
        port = cls._get_port()
        server = IMAP4_SSL(host=imap,
                           port=port,
                           )
        try:
            server.login(login, password)
            return server
        except IMAP4.error as error:
            if not form:
                raise FailConnection(error)
            form.add_error(field=None, error=error)

    def __enter__(self) -> list[int]:
        return self.messages

    def __getitem__(self, index):
        return self.messages[index]

    def __len__(self):
        return len(self.messages)

    def __reverse__(self):
        for i in reversed(range(len(self.messages))):
            yield self.messages[i]

    def reverse(self):
        sequence = self.messages
        n = len(sequence)
        for i in range(n//2):
            sequence[i], sequence[n-i-1] = sequence[n-i-1], sequence[i]

    def action(self) -> list[int]:
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
            )[0].split()
        return self.messages
