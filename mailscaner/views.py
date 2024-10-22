from django.views.generic import TemplateView
from django.contrib.auth import mixins


class MainPageView(mixins.LoginRequiredMixin, TemplateView):
    """
    View основной страницы
    """
    template_name = 'mailscaner/main.html'
