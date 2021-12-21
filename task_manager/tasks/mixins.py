from typing import Any, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated."""

    redirect_field_name = ''
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.
        Args:
            request:
        Returns:
            Any:
        """
        if not request.user.is_authenticated:
            messages.error(request, _('UserNotAuthentication'))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CheckUserRightsTestMixin(UserPassesTestMixin):
    """Deny a request with a permission error if the test_func() == False."""

    redirect_url = settings.LOGIN_REDIRECT_URL

    def handle_no_permission(self) -> Union[  # noqa: WPS320
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    ]:
        """
        Handle no permission.
        Returns:
            Union:
        """
        return redirect(self.redirect_url)

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.
        Args:
            request:
        Returns:
            Any:
        """
        user_test_result = self.get_test_func()()

        if not request.user.is_authenticated:
            self.redirect_url = reverse_lazy('login')  # noqa: WPS601
            messages.error(request, _('UserNotAuthentication'))
            return self.handle_no_permission()
        if not user_test_result:
            messages.error(request, _('ErrorTaskCanOnlyBeDeletedByAuthor'))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
