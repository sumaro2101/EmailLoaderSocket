import json
from channels.generic.websocket import AsyncWebsocketConsumer

from django.db.models import Q

from .models import Email


class DownloadMessagesConsumer(AsyncWebsocketConsumer):
    """
    Потребитель загрузок сообщений
    """

    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['mail_id']
        self.group_ids = f'email_{self.id}'

        await self.channel_layer.group_add(
            self.group_ids,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.group_ids,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_json = json.loads(text_data)
        id_ = text_json['id']
        await self.channel_layer.group_send(
            self.group_ids,
            {
                'type': 'send_number',
                'number': id_,
            },
        )
        await self.channel_layer.group_send(
            self.group_ids,
            {
                'type': 'send_data',
                'reverse_number': id_,
                'title': 'title',
                'date_sending': '20/11/2023',
                'date_receipt': '20/12/2024',
                'text': 'some_text',
                'file': 'file.json',
            },
        )

    async def send_data(self, event):
        reverse_number = event['reverse_number']
        title = event['title']
        date_sending = event['date_sending']
        date_receipt = event['date_receipt']
        text = event['text']
        file_ = event['file']
        await self.send(text_data=json.dumps({
            'reverse_number': reverse_number,
            'title': title,
            'date_sending': date_sending,
            'date_receipt': date_receipt,
            'text': text,
            'file': file_,
        }))

    async def send_number(self, event):
        number = event['number']
        await self.send(text_data=json.dumps({
            'number': number,
        }))
