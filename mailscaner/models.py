from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


CurrentUser = get_user_model()


class Email(models.Model):
    """
    Модель Эмеила
    """
    address = models.EmailField(max_length=254,
                                verbose_name='email',
                                help_text='Email',
                                )
    password = models.CharField(max_length=254,
                                verbose_name='password',
                                help_text='Пароль от почты',
                                )

    user = models.ForeignKey(CurrentUser,
                             verbose_name='пользователь',
                             on_delete=models.CASCADE,
                             related_name='user_emails',
                             help_text='Текущий пользователь',
                             )

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return self.address


class Message(models.Model):
    """
    Модель сообщения из эмеила
    """
    title = models.CharField(max_length=254,
                             verbose_name='тема',
                             help_text='Тема сообщения',
                             )
    date_sending = models.DateTimeField(verbose_name='дата отправки',
                                        help_text='Дата отправки сообщения',
                                        )
    date_receipt = models.DateTimeField(verbose_name='дата получения',
                                        help_text='Дата получения сообщения',
                                        )
    text = models.TextField(verbose_name='текст сообщения',
                            help_text='Текст из сообщения',
                            )
    file = models.FileField(upload_to=f'{date_receipt}/{title}/',
                            verbose_name='файл',
                            help_text='Файл из сообщения, если есть',
                            null=True,
                            blank=True,
                            )

    email = models.ForeignKey(Email,
                              on_delete=models.CASCADE,
                              verbose_name='эмеил',
                              related_name='messages',
                              help_text='Эмеил к которому относится сообщение',
                              )

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return self.date_receipt

    def get_absolute_url(self):
        return reverse("message_detail", kwargs={"pk": self.pk})
