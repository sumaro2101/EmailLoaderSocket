from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import (TemplateView,
                                  CreateView,
                                  ListView,
                                  )
from django.contrib.auth import mixins
from django.urls import reverse_lazy
from django.db.models import Q

from .forms import EmailCreateFrom
from .models import Email


class MainPageView(mixins.LoginRequiredMixin, TemplateView):
    """
    View основной страницы
    """
    template_name = 'mailscaner/main.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Main')
        return context


class CreateEmailView(mixins.LoginRequiredMixin, CreateView):
    """
    View создания эмеила
    """
    form_class = EmailCreateFrom
    template_name = 'mailscaner/email_create.html'
    success_url = reverse_lazy('mailscaner/done')

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Create Email')
        return context


class DoneCreateEmailView(mixins.LoginRequiredMixin, TemplateView):
    """
    View завершения создания эмеила
    """
    template_name = 'mailscaner/done.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Done')
        return context


class EmailListView(mixins.LoginRequiredMixin, ListView):
    """
    View просмотра списка эмеилов пользователя
    """
    context_object_name = 'emails'
    template_name = 'mailscaner/emails.html'

    def get_queryset(self) -> QuerySet[Any]:
        path = self.request.path.split('/')
        type_email = '@' + path[-2]
        self.queryset = (Email
                        .objects
                        .filter(Q(address__contains=type_email)&
                                Q(user=self.request.user)))
        return self.queryset    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='List Emails')
        return context
