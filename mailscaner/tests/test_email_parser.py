from imaplib import IMAP4_SSL

from django.test import TestCase
from django.conf import settings

from mailscaner.mail_parser import Parser
from mailscaner.mail_parser.connections import GmailConnection


TEST_EMAIL = settings.TEST_EMAIL_HOST_GMAIL
TEST_PASSWORD = settings.TEST_EMAIL_PASSWORD_GMAIL

messages = GmailConnection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
            limit=1,
            )

class TestEmailParser(TestCase):
    """
    Тесты парсера эмеила
    """
    def setUp(self) -> None:
        self.messages = messages

    def test_check_connection(self):
        connection = GmailConnection.connection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
        )
        self.assertIsInstance(connection, IMAP4_SSL)

    def test_limit(self):
        self.assertEqual(len(self.messages), 1)
    
    def test_parse_date(self):
        pass