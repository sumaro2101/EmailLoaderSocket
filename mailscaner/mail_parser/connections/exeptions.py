class FailConnection(Exception):
    """
    Исключение не удавшегося подключения
    """

    pass


class BaseConnectionError(Exception):
    """
    Исключение использования базового класса подключения
    """

    pass
