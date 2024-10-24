from abc import ABC, abstractmethod
from django.forms import BaseForm

from typing import Any, Literal


class AbstractConnection(ABC):
    """
    Абстрактное представление соединения
    с Эмеил почтой
    """

    @abstractmethod
    def __init__(self, login: str, password: str) -> None:
        pass

    @abstractmethod
    def select_box(self,
                   box: Literal['INBOX',
                                'FLAGS',
                                'EXISTS',
                                'RECENT',
                                'UIDVALIDITY',
                                ] = 'INBOX',
                   ) -> tuple[str, list[bytes | None]]:
        pass

    @abstractmethod
    def search_data(charset: str | None = None,
                    criteria: str = 'ALL',
                    ) -> (tuple[Literal['NO'], Any] | tuple[Any, list[None]] | tuple):
        pass

    @abstractmethod
    @classmethod
    def connection(cls,
                   form: BaseForm | None = None,
                   ) -> tuple[Literal['OK'], list[bytes]]:
        pass

    @abstractmethod
    def __enter__(self) -> (tuple[Literal['NO'], Any] | tuple[Any, list[None]] | tuple):
        pass
