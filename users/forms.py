from django.contrib.auth.forms import (AuthenticationForm,
                                       UserCreationForm,
                                       )
from django.contrib.auth import get_user_model
from django import forms


class UserAuthenticationForm(AuthenticationForm):
    """
    Форма Аутентификации пользователя
    """
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = ('username', 'password',)


class UserRegisterForm(UserCreationForm):
    """
    Форма Регистрация пользователя
    """

    class Meta:
        model = get_user_model()
        fields = ('username',
                  'email',
                  'password1',
                  'password2',
                  )
