from typing import Any, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class CheckUserRightsTestMixin(UserPassesTestMixin):
    """Deny a request with a permission error if the test_func() == False."""

    redirect_url = settings.LOGIN_REDIRECT_URL

    def test_func(self) -> bool:
        """
        Test function.
        Returns:
            bool:
        """
        return self.get_object() == self.request.user

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
            self.redirect_url = reverse_lazy('users')  # noqa: WPS601
            messages.error(request, _('UserNotHaveRights'))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
