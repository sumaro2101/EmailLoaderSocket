import base64
from datetime import datetime
import email
import email.header
import email.parser
import email.utils
import re
import io

from imaplib import IMAP4_SSL

from loguru import logger

from email.message import Message
import quopri

from bs4 import BeautifulSoup
from bs4.element import ResultSet

from django.conf import settings
from django.core.files import File


class Parser:
    """
    Парсер сообщений
    """
    __RFC = settings.RFC822

    def __init__(self,
                 connection: IMAP4_SSL,
                 uid: bytes,
                 ) -> None:
        self.server = connection
        self.uid = uid
        self.TextParser = TextParser
        self.FileParser = FileParser

    def _date_parse(self, mess_date: str) -> datetime | None:
        """
        ["Date"]
        """
        logger.debug(f'_date_parse to start {mess_date}')
        parse_date_tz = email.utils.parsedate_tz(mess_date)
        if parse_date_tz:
            stringify_date = ''.join(str(parse_date_tz[:6]))
            clear_time = stringify_date.strip("'(),")
            datetime_type = datetime.strptime(
                clear_time, '%Y, %m, %d, %H, %M, %S',
                )
            logger.debug(f'_date_parse to end {datetime_type}')
            return datetime_type
        logger.debug(f'_date_parse to end {mess_date}')
        return None

    def _subject_parse(self, subject: str) -> str:
        """
        ["Subject"]
        """
        if subject:
            subject_bytes = email.header.decode_header(subject)
            codec, data = subject_bytes[0][-1], subject_bytes[0][0]
            if isinstance(data, bytes):
                logger.debug('data is bytest')
                if codec:
                    if codec == 'iso-8859-8-i':
                        codec = 'iso-8859-8'
                        deconed_subject = data.decode(encoding=codec)
                    elif codec == 'unknown-8bit':
                        logger.debug(f'enter to codec {codec}')
                        logger.debug(data)
                        try:
                            deconed_subject = data.decode(
                                encoding='utf-8',
                                )
                        except UnicodeDecodeError:
                            deconed_subject = data.decode(
                                encoding='iso-8859-8',
                                )
                    else:
                        deconed_subject = data.decode(encoding=codec)
                        logger.debug(f'decoded {deconed_subject}')
                else:
                    deconed_subject = data
            if isinstance(data, str):
                deconed_subject = data
            logger.debug(data)
            clear_subject = str(deconed_subject).strip('<>').replace('<', '')
            logger.debug(f'_subject_parse get {clear_subject}')
            return clear_subject

    def _return_path_parse(self, from_: str) -> str:
        """
        ["Return-path"]
        """
        if from_:
            from_email = from_.lstrip('<').rsplit('>')[0]
            logger.debug(f'_return_path_parse get {from_email}')
            return from_email

    def parse(self):
        res, msg = self.server.fetch(self.uid, self.__RFC)
        if res == 'OK':
            msg = email.message_from_bytes(msg[0][1])
            title = self._subject_parse(msg['Subject'])
            sender = self._return_path_parse(msg['Return-path'])
            date_sending = self._date_parse(msg['Date'])
            date_receipt = self._date_parse(msg['Received'].split(';')[-1])
            text = self.TextParser(msg).parse()
            files = self.FileParser(msg).parse()
            logger.info(f'title is {title}')
            logger.info(f'sender if {sender}')
            logger.info(f'date_sendin is {date_sending}')
            logger.info(f'date_receipt is {date_receipt}')
            logger.info(f'text is {text}')
            logger.info(f'files is {files}')
            values = dict(
                title=title,
                sender=sender,
                date_sending=date_sending,
                date_receipt=date_receipt,
                text=text,
                files=files,
            )
            return values


class TextParser:
    """
    Парсер текста сообщения
    """
    def __init__(self, message: Message) -> None:
        self.message = message

    @logger.catch(reraise=True)
    def _get_extract_part(self, part: Message):
        payload = part.get_payload()
        if (part["Content-Transfer-Encoding"] in
           (None, "7bit", "8bit", "binary")):
            return payload
        elif part["Content-Transfer-Encoding"] == "base64":
            encoding = part.get_content_charset()
            if not encoding or encoding == 'utf8':
                encoding = 'utf-8'
            payload = (base64.b64decode(payload)
                       .decode(encoding=encoding,
                               errors='ignore',
                               ))
            return payload
        elif part["Content-Transfer-Encoding"] == "quoted-printable":
            encoding = part.get_content_charset()
            if encoding == 'iso-8859-8-i':
                encoding = 'iso-8859-8'
            payload = quopri.decodestring(payload).decode(encoding=encoding)
            return payload
        else:
            return payload

    @logger.catch(reraise=True)
    def _parse_html(self, part: str) -> str:
        body = (part
                .replace('<div><div>', '<div>')
                .replace('</div></div>', '</div>')
                .replace('\n', ' '))
        soup = BeautifulSoup(body, 'html.parser')
        paragraphs: ResultSet = soup.find_all('div')
        if paragraphs:
            text = ' '.join([litter
                             for litter
                             in (paragraphs[0].text).split(' ')
                             if litter])
        else:
            return ''
        logger.debug(f'paragraphs is {text}')
        return text

    @logger.catch(reraise=True)
    def _parse_text(self, target: Message) -> str:
        maintype = target.get_content_maintype()
        subtype = target.get_content_subtype()
        logger.info(f'maintype is {maintype}')
        logger.info(f'subtype is {subtype}')
        if maintype == 'text':
            extract_part = self._get_extract_part(target)
            if subtype == 'html':
                letter_text = self._parse_html(extract_part)
            else:
                letter_text = extract_part.rstrip().lstrip()
            return (letter_text
                    .replace('<', '')
                    .replace('>', '')
                    .replace('\xa0', ' ')
                    .replace('\n', ' '))

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

    @logger.catch(reraise=True)
    def _get_name_file(self, str_playload) -> str:
        logger.info(f'_get_name_file get part {str_playload}')
        enode_name = re.findall("\=\?.*?\?\=", str_playload)
        if len(enode_name) == 1:
            logger.info('len enode_name 1')
            value = enode_name[0]
            encoding = email.header.decode_header(value)[0][1]
            if encoding == 'iso-8859-8-i':
                encoding = 'iso-8859-8'
            decode_name = email.header.decode_header(value)[0][0]
            decode_name = decode_name.decode(encoding)
            str_playload = str_playload.replace(value, decode_name)
            logger.info(f'return name {str_playload}')
        if len(enode_name) > 1:
            logger.info('len enode_name more then 1')
            nm = ""
            value = enode_name[0]
            for name in enode_name:
                encoding = email.header.decode_header(name)[0][1]
                decode_name = email.header.decode_header(name)[0][0]
                if encoding:
                    try:
                        decode_name = decode_name.decode(encoding)
                    except UnicodeDecodeError:
                        decode_name = decode_name.decode(encoding='iso-8859-1')
                    nm += decode_name
                logger.info(f'return composite name {nm}')
            str_playload = str_playload.replace(value, nm)
            for c, i in enumerate(enode_name):
                if c > 0:
                    str_playload = (str_playload.
                                    replace(enode_name[c], "").
                                    replace('"', "").rstrip())
        return str_playload.split(';')[-1].replace('name=', '')

    @logger.catch(reraise=True)
    def _get_attachments(self, message: Message) -> list[File]:
        for part in message.walk():
            disposition = part.get_content_disposition()
            content_type = part['Content-Type']
            logger.info(f'file class disposition {disposition}')
            logger.info(f'file class content_type {content_type}')
            if (content_type and
               'name' in content_type and
               disposition == 'attachment'):
                name = self._get_name_file(content_type)
                logger.info(f'name file is {name}')
                payload: bytes = base64.b64decode(part.get_payload())
                file = File(file=io.BytesIO(payload),
                            name=(name.strip()
                                  .replace('"', '')
                                  .replace('_', '-')
                                  .replace(' ', '-')
                                  .replace('--', '-')
                                  .replace('/', '-')
                                  .replace(':', '')))
                logger.info(f'set file {file}')
                self.attachments.append(file)
        return self.attachments

    def parse(self) -> list[File]:
        """
        Парсит файл из полученного сообщения
        """
        files = self._get_attachments(self.message)
        return files
