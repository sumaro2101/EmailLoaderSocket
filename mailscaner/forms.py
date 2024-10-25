from typing import Any
from django import forms
from django.db.models import Q

from .models import Email
from .regex import check_email_type
from .mail_parser.connections import (
    GmailConnection,
    MailConnection,
    YandexConnection,
)


class EmailCreateFrom(forms.ModelForm):
    """
    Форма создания эмеила
    """
    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Email
        fields = ('address', 'password')

    def clean_address(self):
        address = self.cleaned_data.get('address')
        correct = check_email_type(address)
        if not correct:
            self.add_error('address',
                           'Provide @yandex.ru, @mail.ru or @gmail.com',
                           )
        return address

    def clean(self) -> dict[str, Any]:
        address = self.cleaned_data.get('address')
        password = self.cleaned_data.get('password')
        dublicate = (Email
                     .objects
                     .filter(Q(address=address)
                             & Q(user=self.user))
                     .exists())
        if dublicate:
            self.add_error(
                'address',
                'This Email exists for this user',
            )

        match address.split('@'):
            case _, email_type if email_type == 'yandex.ru':
                YandexConnection.connection(
                    login=address,
                    password=password,
                    form=self,
                )
            case _, email_type if email_type == 'mail.ru':
                MailConnection.connection(
                    login=address,
                    password=password,
                    form=self,
                )
            case _, email_type if email_type == 'gmail.com':
                GmailConnection.connection(
                    login=address,
                    password=password,
                    form=self,
                )

        return self.cleaned_data

    def save(self, commit: bool = ...) -> Any:
        self.instance.user = self.user
        return super().save(commit)
