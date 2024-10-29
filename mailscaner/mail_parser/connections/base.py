from imaplib import IMAP4_SSL, IMAP4
from typing import Any, Literal

from django.conf import settings
from django.forms import BaseForm
import socket
import time

from loguru import logger

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
                 limit: bytes | None = None,
                 set_reverse: bool = True,
                 ) -> None:
        self.__login = login
        self.__password = password
        self.mailbox = mailbox
        self.charset = charset
        self.criteria = criteria
        self.limit = limit
        self.set_reverse = set_reverse
        self.server: IMAP4_SSL = None
        self.__online = False
        self.messages = self._action()

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
        status, data = self.server.search(charset, criteria)
        return data

    def _set_limit(self,
                   limit: bytes | None,
                   ) -> None:
        if limit:
            value = bytes(limit)
            index = self.messages.index(value)
            self.messages = self[:index]

    def _set_reverse(self,
                     reverse: bool,
                     ) -> None:
        if reverse:
            self.reverse()

    @property
    def online(self):
        return self.__online

    @classmethod
    @logger.catch(reraise=True)
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
        logger.debug(f'imap get {imap}')
        logger.debug(f'port {port}')
        connect = False
        while not connect:
            try:
                server = IMAP4_SSL(host=imap,
                                   port=port,
                                   )
                connect = True
            except socket.gaierror:
                logger.warning('No have connecting, try 3 seconds')
                time.sleep(3)
        try:
            server.login(login, password)
            cls.__online = True
            return server
        except IMAP4.error as error:
            message = error.args[0].decode()
            if not form:
                raise FailConnection(message)
            form.add_error(field=None, error=message)

    def __enter__(self) -> list[bytes]:
        return self

    def __exit__(self, *args):
        self.server.close()
        self.server.logout()

    def __getitem__(self, index):
        return self.messages[index]

    def __len__(self):
        return len(self.messages)

    def __reverse__(self):
        for i in reversed(range(len(self.messages))):
            yield self.messages[i]

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1
        except IndexError:
            return

    def reverse(self):
        messages = self.messages
        n = len(self)
        for i in range(n//2):
            messages[i], messages[n-i-1] = messages[n-i-1], messages[i]

    def _action(self) -> list[bytes]:
        """
        Создание подключения с настройками
        """
        self.server = self.connection(
            login=self.__login,
            password=self.__password,
        )
        self.__online = True
        self._select_box(box=self.mailbox)
        self.messages = self._search_data(
            charset=self.charset,
            criteria=self.criteria,
            )[0].split()
        self._set_reverse(self.set_reverse)
        self._set_limit(self.limit)
        return self.messages
