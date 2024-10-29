from imaplib import IMAP4_SSL


from django.test import TestCase
from django.conf import settings

from mailscaner.mail_parser import Parser
from mailscaner.mail_parser.connections import GmailConnection


TEST_EMAIL = settings.TEST_EMAIL_HOST_GMAIL
TEST_PASSWORD = settings.TEST_EMAIL_PASSWORD_GMAIL


connect = GmailConnection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
            # limit=2,
            )

parser = Parser(connection=connect)


class TestEmailParser(TestCase):
    """
    Тесты парсера эмеила
    """
    def setUp(self) -> None:
        self.messages = connect
        self.parser = parser
        self.message = parser.messages[0]

    def test_check_connection(self):
        connection = GmailConnection.connection(
            login=TEST_EMAIL,
            password=TEST_PASSWORD,
        )
        self.assertIsInstance(connection, IMAP4_SSL)

    def test_limit(self):
        self.assertEqual(len(self.messages), 1)

    # def test_parse_date(self):
    #     value = parser._date_parse(self.message['Date'])
    #     self.assertEqual(value, 0)

    def test_parser(self):
        generator = parser.load_messages()
        value = None
        for item in generator:
            value = item
        self.assertEqual(len(value), 7)
        self.parser.server.logout()
