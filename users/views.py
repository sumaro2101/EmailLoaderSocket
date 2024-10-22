from typing import Any
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import (CreateView,
                                  DetailView,
                                  TemplateView,
                                  )

from .forms import (UserRegisterForm,
                    UserAuthenticationForm,
                    )


UserModel = get_user_model()


class AuthView(LoginView):
    """
    View Аутентификации
    """
    template_name = 'users/login.html'
    form_class = UserAuthenticationForm

    def get_success_url(self) -> str:
        return reverse_lazy('mailscaner:main')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Authentication')
        return context


class RegistrationView(CreateView):
    """
    View Регистрации пользователя
    """
    template_name = 'users/registration.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:done')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title='Registration')
        return context


class UserDetailView(DetailView):
    """
    View профиля пользователя
    """
    model = UserModel
    template_name = 'users/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'current_user'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(title=self.object.username)
        return context


class DoneRegistationView(TemplateView):
    """
    View завершения регистрации
    """
    template_name = 'users/done.html'
