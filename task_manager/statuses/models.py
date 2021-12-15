from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    """Status model."""

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_('StatusName'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        String representation.

        Returns:
             str:
        """
        return self.name

    class Meta(object):
        """Meta information."""

        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['name']
