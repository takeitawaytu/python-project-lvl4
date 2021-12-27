from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom user."""

    first_name = models.CharField(
        _('first name'),
        max_length=150,
        error_messages={
            'blank': _('ThisFieldCannotBeBlank'),
        },
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        error_messages={
            'blank': _('ThisFieldCannotBeBlank'),
        },
    )

    def get_absolute_url(self):  # noqa: D102
        return reverse_lazy('update_user', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        """
        String representation.
        Returns:
            str:
        """
        return self.get_full_name()

    class Meta:  # noqa: WPS306
        """Meta information."""

        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
