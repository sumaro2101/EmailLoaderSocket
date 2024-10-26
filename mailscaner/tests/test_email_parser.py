from django.test import TestCase
from django.conf import settings

from mailscaner.mail_parser import Parser
from mailscaner.mail_parser.connections import GmailConnection


TEST_EMAIL = settings.TEST_EMAIL_HOST_GMAIL
TEST_PASSWORD = settings.TEST_EMAIL_PASSWORD_GMAIL


class TestEmailParser(TestCase):
    """
    Тесты парсера эмеила
    """
    def setUp(self) -> None:
        self.server = GmailConnection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
        )
    
    def check_connection(self):
        connection = GmailConnection.connection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
        )
        self.assertIsNone(connection)
