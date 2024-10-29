from django.urls import path

from .apps import MailscanerConfig
from . import views


app_name = MailscanerConfig.name


urlpatterns = [
    path('',
         views.MainPageView.as_view(),
         name='main',
         ),
    path('email/create/',
         views.CreateEmailView.as_view(),
         name='create',
         ),
    path('email/delete/<int:pk>/',
         views.DeleteEmailView.as_view(),
         name='delete',
         ),
    path('email/done/',
         views.DoneCreateEmailView.as_view(),
         name='done',
         ),
    path('email/yandex/',
         views.EmailListView.as_view(),
         name='yandex',
         ),
    path('email/gmail/',
         views.EmailListView.as_view(),
         name='gmail',
         ),
    path('email/mail/',
         views.EmailListView.as_view(),
         name='mail',
         ),
    path('email/download/<int:pk>/',
         views.MessagesDownloadView.as_view(),
         name='download',
         ),
    path('email/message/<int:pk>/',
         views.MessageDetailView.as_view(),
         name='message',
         ),
    path('email/messages/<int:pk>/',
         views.MessagesListView.as_view(),
         name='messages',
         ),
]
