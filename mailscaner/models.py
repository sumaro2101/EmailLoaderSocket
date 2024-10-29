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
    last_index = models.BinaryField(null=True,
                                    blank=True,
                                    verbose_name='последний индекс',
                                    help_text='Последний uid выгруженного '
                                    'из почты',
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
        constraints = [
            models.UniqueConstraint(
                fields=('user_id', 'address'),
                name='unique_user_address_constraint'
            )
        ]

    def __str__(self):
        return self.address


class File(models.Model):
    """
    Модель файла
    """
    name = models.CharField(max_length=245,
                            verbose_name='имя',
                            help_text='Имя сохраненного файла',
                            )
    file = models.FileField(upload_to='images/',
                            verbose_name='файл',
                            help_text='Файл из сообщения, если есть',
                            null=True,
                            blank=True,
                            max_length=300,
                            )

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("file_detail", kwargs={"pk": self.pk})


class Message(models.Model):
    """
    Модель сообщения из эмеила
    """
    title = models.CharField(max_length=254,
                             verbose_name='тема',
                             help_text='Тема сообщения',
                             null=True,
                             blank=True,
                             )
    sender = models.EmailField(max_length=254,
                               verbose_name='отправитель',
                               help_text='Отправитель письма',
                               null=True,
                               blank=True,
                               )
    date_sending = models.DateTimeField(verbose_name='дата отправки',
                                        help_text='Дата отправки сообщения',
                                        )
    date_receipt = models.DateTimeField(verbose_name='дата получения',
                                        help_text='Дата получения сообщения',
                                        )
    text = models.TextField(verbose_name='текст сообщения',
                            help_text='Текст из сообщения',
                            null=True,
                            blank=True,
                            )

    files = models.ManyToManyField(File,
                                   verbose_name='файлы',
                                   help_text='Сохраненые файлы',
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
        return str(self.date_receipt)

    def get_absolute_url(self):
        return reverse("message_detail", kwargs={"pk": self.pk})
