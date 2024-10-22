from django.urls import path

from .apps import MailscanerConfig
from . import views


app_name = MailscanerConfig.name


urlpatterns = [
    path('', views.MainPageView.as_view(), name='main'),
]
