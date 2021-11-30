from django.shortcuts import render
from django.utils.translation import gettext as _


def index(request):
    return render(request, 'base.html', context={
        'BASE_APP_NAME': _('Менеджер задач'),
        'BASE_USERS': _('Пользователи'),
        'BASE_LOGIN': _('Вход'),
        'BASE_SIGNUP': _('Регистрация'),
    })
