from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom user."""

    def get_absolute_url(self):  # noqa: D102
        return reverse_lazy('update_user', kwargs={'pk': self.pk})

    class Meta:  # noqa: WPS306
        """Meta information."""

        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
