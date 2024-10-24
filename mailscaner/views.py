from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.views.generic import (TemplateView,
                                  CreateView,
                                  ListView,
                                  DeleteView,
                                  DetailView,
                                  )
from django.contrib.auth import mixins
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache

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
    success_url = reverse_lazy('mailscaner:done')
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Create Email')
        return context


class DeleteEmailView(mixins.UserPassesTestMixin ,mixins.LoginRequiredMixin, DeleteView):
    """
    View удаления Эмеила
    """
    model = Email
    context_object_name = 'email'
    template_name = 'mailscaner/delete_mail.html'
    
    def get_success_url(self) -> str:
        return reverse_lazy(f'mailscaner:{self.path}')

    def test_func(self) -> bool | None:
        self.object = self.get_object()
        self.path = self.object.address.split('@')[-1].split('.')[0]
        return self.object.user == self.request.user


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


class MessagesDownloadView(mixins.UserPassesTestMixin, mixins.LoginRequiredMixin, DetailView):
    """
    View для загрузки сообщений из эмеил
    """
    model = Email
    context_object_name = 'email'
    template_name = 'mailscaner/download.html'

    def test_func(self) -> bool | None:
        object_ = self.get_object()
        return object_.user == self.request.user
