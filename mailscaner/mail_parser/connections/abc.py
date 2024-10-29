from abc import ABC, abstractmethod
from imaplib import IMAP4_SSL
from django.forms import BaseForm

from typing import Any, Literal


class AbstractConnection(ABC):
    """
    Абстрактное представление соединения
    с Эмеил почтой
    """

    @abstractmethod
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
                 criteria: str = 'ALL'
                 ) -> None:
        pass

    @abstractmethod
    def _select_box(self,
                    box: str,
                    ) -> tuple[str, list[bytes | None]]:
        pass

    @abstractmethod
    def _search_data(self,
                     charset: str | None,
                     criteria: str,
                     ) -> (tuple[Literal['NO'], Any] |
                           tuple[Any, list[None]] |
                           tuple):
        pass

    @classmethod
    @abstractmethod
    def connection(cls,
                   login: str,
                   password: str,
                   form: BaseForm | None = None,
                   ) -> IMAP4_SSL:
        pass

    @abstractmethod
    def __enter__(self) -> list[int]:
        pass
