import json
from channels.generic.websocket import AsyncWebsocketConsumer

from loguru import logger

from django.db.models import Q

from .models import Email, Message, File
from .mail_parser.connections import (
    GmailConnection,
    YandexConnection,
    MailConnection,
)
from .mail_parser import Parser


class DownloadMessagesConsumer(AsyncWebsocketConsumer):
    """
    Потребитель загрузок сообщений
    """

    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['mail_id']
        user = self.scope['user']
        self.group_id = f'email{self.id}'
        await self.channel_layer.group_add(
            self.group_id,
            self.channel_name,
        )
        await self.accept()
        self.email = await Email.objects.aget(Q(pk=self.id) &
                                              Q(user=user))
        match self.email.address.split('@'):
            case _, 'yandex.ru':
                logger.info('email yandex.ru')
                server = YandexConnection
            case _, 'mail.ru':
                logger.info('email mail.ru')
                server = MailConnection
            case _, 'gmail.com':
                logger.info('email gmail.com')
                server = GmailConnection
        self.connection = server(
            self.email.address,
            self.email.password,
            limit=self.email.last_index,
            )
        list_uids = [id_.decode(encoding='utf-8')
                     for id_
                     in self.connection]
        self.count_items = len(list_uids)
        self.num_summary = 0
        self.items_to_save = list()
        await self.channel_layer.group_send(
            self.group_id,
            {
                'type': 'send_number',
                'list_uids': list_uids,
            },
        )

    async def disconnect(self, code):
        logger.warning('disconnect')
        await self.channel_layer.group_discard(
            self.group_id,
            self.channel_name
        )
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        logger.debug(json_data)
        uid = json_data['uid'].encode(encoding='utf-8')
        parser = Parser(self.connection.server, uid)
        message = parser.parse()
        date_sending = str(message['date_sending'])
        date_receipt = str(message['date_receipt'])
        files = [file.name for file in message['files']]
        values = message.copy()
        values.pop('files')
        self.items_to_save.append(Message(
            email=self.email,
            **values,
        ))
        self.num_summary += 1
        if files:
            to_create = [File(name=file.name, file=file)
                         for file
                         in message['files']]
            created = await File.objects.abulk_create(to_create)
            files_to_save = [file.id for file in created]
            logger.debug(f'get to create files {to_create}')
            item: Message = self.items_to_save.pop()
            logger.debug(f'pop item is {item}')
            await item.asave()
            [await item.files.aadd(file)
             for file
             in files_to_save]
        procent = format((self.num_summary / self.count_items * 100),
                         '.2f',
                         )
        values = {
                'type': 'send_data',
                'count': (self.count_items - self.num_summary) + 1,
                'reverse_number': self.num_summary,
                'procent': procent,
                'title': message['title'],
                'sender': message['sender'],
                'date_sending': date_sending,
                'date_receipt': date_receipt,
                'text': message['text'],
                'files': files,
            }
        await self.channel_layer.group_send(
            self.group_id,
            values,
        )
        logger.warning(f'{self.num_summary} is sended')

        if (len(self.items_to_save) == 10 or
           self.num_summary == self.count_items):
            logger.warning(f'last index the {uid}')
            await Message.objects.abulk_create(self.items_to_save)
            self.email.last_index = uid
            await self.email.asave()
            self.items_to_save.clear()

    async def send_data(self, event):
        count = event['count']
        reverse_number = event['reverse_number']
        procent = event['procent']
        title = event['title']
        sender = event['sender']
        date_sending = event['date_sending']
        date_receipt = event['date_receipt']
        text = event['text']
        files = event['files']
        logger.warning(f'{reverse_number} wait to front')
        await self.send(text_data=json.dumps({
            'count': count,
            'reverse_number': reverse_number,
            'procent': procent,
            'title': title,
            'sender': sender,
            'date_sending': date_sending,
            'date_receipt': date_receipt,
            'text': text,
            'files': files,
        }))
        logger.warning(f'{reverse_number} is send to front')

    async def send_number(self, event):
        list_uids = event['list_uids']
        await self.send(text_data=json.dumps({
            'list_uids': list_uids,
        }))
        logger.info('list is sended')
