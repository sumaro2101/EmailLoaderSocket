from django.contrib import admin

from .models import Message


@admin.register(Message)
class AdminMessageView(admin.ModelAdmin):
    list_display = (
        'title',
        'sender',
        'date_sending',
        'date_receipt',
        'text',
        'email',
    )
    list_select_related = ('email',)
    filter_horizontal = (
        'files',
    )
