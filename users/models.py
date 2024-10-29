from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Модель пользователя
    """
    image = models.ImageField(upload_to='users/',
                              blank=True,
                              null=True,
                              verbose_name='Изображение',
                              help_text='Изображение пользователя',
                              )

    emails = models.ManyToManyField("mailscaner.Email",
                                    verbose_name='эмеилы',
                                    help_text='Эмеилы '
                                    'принадлежащие пользователю',
                                    related_name='users',
                                    )

    class Meta:
        db_table = 'user'
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def get_absolute_url(self):
        return reverse("users:user", kwargs={"username": self.username})
