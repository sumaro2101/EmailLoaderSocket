from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    re_path(r'email/download/(?P<mail_id>\d+)/$',
            consumers.DownloadMessagesConsumer.as_asgi(),
            ),
]
