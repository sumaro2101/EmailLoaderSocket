# Generated by Django 5.1.2 on 2024-10-23 10:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.EmailField(help_text='Email', max_length=254, verbose_name='email')),
                ('password', models.CharField(help_text='Пароль от почты', max_length=254, verbose_name='пароль')),
                ('user', models.ForeignKey(help_text='Текущий пользователь', on_delete=django.db.models.deletion.CASCADE, related_name='user_emails', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Тема сообщения', max_length=254, verbose_name='тема')),
                ('date_sending', models.DateTimeField(help_text='Дата отправки сообщения', verbose_name='дата отправки')),
                ('date_receipt', models.DateTimeField(help_text='Дата получения сообщения', verbose_name='дата получения')),
                ('text', models.TextField(help_text='Текст из сообщения', verbose_name='текст сообщения')),
                ('file', models.FileField(blank=True, help_text='Файл из сообщения, если есть', null=True, upload_to='<django.db.models.fields.DateTimeField>/<django.db.models.fields.CharField>/', verbose_name='файл')),
                ('email', models.ForeignKey(help_text='Эмеил к которому относится сообщение', on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='mailscaner.email', verbose_name='эмеил')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
    ]
