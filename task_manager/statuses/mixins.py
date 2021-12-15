from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
