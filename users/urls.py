from django.urls import path

from django.contrib.auth.views import LogoutView

from .apps import UsersConfig
from . import views


app_name = UsersConfig.name


urlpatterns = [
    path("login/", views.AuthView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('done/', views.DoneRegistationView.as_view(), name='done'),
    path('registration/', views.RegistrationView.as_view(), name='reg'),
    path('user/<str:username>/', views.UserDetailView.as_view(), name='user'),
]
