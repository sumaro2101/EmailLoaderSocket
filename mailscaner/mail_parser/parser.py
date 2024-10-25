import base64
from datetime import datetime
import email
import email.header
import email.parser
import email.utils

from email.message import Message
import quopri

from bs4 import BeautifulSoup
from bs4.element import ResultSet

from django.conf import settings
from django.core.files import File
from .connections.base import BaseConnection


class Parser:
    """
    Парсер сообщений
    """
    from_end_to_start = True
    __RFC = settings.RFC822
    __decode = settings.DECODER

    def __init__(self,
                 connection: BaseConnection
                 ) -> None:
        self.messages = connection
        self.server = connection.server
        self.TextParser = TextParser
        self.FileParser = FileParser

    def _date_parse(self, mess_date: str) -> datetime | None:
        """
        ["Date"]
        """
        parse_date_tz = email.utils.parsedate_tz(mess_date)
        if parse_date_tz:
            stringify_date = ''.join(str(parse_date_tz[:6]))
            clear_time = stringify_date.strip("'(),")
            datetime_type = datetime.strptime(clear_time, '%Y, %m, %d, %H, %M, %S')
            return datetime_type
        return None

    def _subject_parse(self, subject: str) -> str:
        """
        ["Subject"]
        """
        if subject:
            subject_bytes = email.header.decode_header(subject)
            codec, data = subject_bytes[0][-1], subject_bytes[0][0]
            if isinstance(data, bytes):
                deconed_subject = data.decode(encoding=codec)
            if isinstance(data, str):
                deconed_subject = data
            clear_subject = str(deconed_subject).strip('<>').replace('<', '')
            return clear_subject

    def _return_path_parse(self, from_: str) -> str:
        """
        ["Return-path"]
        """
        if from_:
            from_email = from_.lstrip('<').rsplit('>')

    def load_messages(self):
        uids = self.messages
        values = dict()
        if self.from_end_to_start:
            uids = reversed(uids)
        for index, uid in enumerate(uids):
            res, msg = self.server.fetch(uid, self.__RFC)
            if res == 'OK':
                msg = email.message_from_bytes(msg[0][1])


class TextParser:
    """
    Парсер текста сообщения
    """
    def __init__(self, message: Message) -> None:
        self.message = message

    def _get_extract_part(self, part: Message):
        payload = part.get_payload()
        if part["Content-Transfer-Encoding"] in (None, "7bit", "8bit", "binary"):
            return payload
        elif part["Content-Transfer-Encoding"] == "base64":
            encoding = part.get_content_charset()
            return base64.b64decode(payload).decode(encoding=encoding)
        elif part["Content-Transfer-Encoding"] == "quoted-printable":
            payload = part.get_payload()
            return quopri.decodestring(payload).decode(encoding=encoding)
        else:
            return payload

    def _parse_html(self, part: str) -> str:
        body = (part
                .replace('<div><div>', '<div>')
                .replace('</div></div>', '</div>'))
        soup = BeautifulSoup(body, 'html.parser')
        paragraphs: ResultSet = soup.find_all('div')
        text = ''
        for part in paragraphs:
            text += part.text + '\n'
        return text.replace('\xa0', ' ')

    def _parse_text(self, target: Message) -> str:
        maintype = target.get_content_maintype()
        subtype = target.get_content_subtype()
        if maintype == 'text':
            extract_part = self._get_extract_part(target)
            if subtype == 'html':
                letter_text = self._parse_html(extract_part)
            else:
                letter_text = extract_part.rstrip().lstrip()
            return (letter_text
                    .replace('<', '')
                    .replace('>', '')
                    .replace('\xa0', ' '))

    def parse(self):
        """
        Парсит текст из полученного сообщения
        """
        message = self.message
        if not message.is_multipart():
            return self._parse_text(message)
        for part in message.walk():
            parse = self._parse_text(part)
            if parse:
                return parse


class FileParser:
    """
    Парсер файлов
    """
    def __init__(self, message: Message) -> None:
        self.message = message
        self.attachments = list()

    def parse(self):
        """
        Парсит файл из полученного сообщения
        """
        