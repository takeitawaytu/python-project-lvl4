from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import gettext as _


def index(request) -> HttpResponse:
    """
    Test.
    Args:
        request: request
    Returns:
        HttpResponse:
    """
    return render(request, 'home.html', context={
        'BASE_APP_NAME': _('TaskManager'),
    })
