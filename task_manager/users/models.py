from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom user."""

    class Meta:  # noqa: WPS306
        """Meta information."""

        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
