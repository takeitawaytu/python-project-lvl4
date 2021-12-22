from django.db import models
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    """Label model."""

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_('LabelName'),
        help_text=_('HelpLabelFieldText'),
        error_messages={
            'unique': _('LabelWithThisNameAlreadyExist'),
            'blank': _('ThisFieldCannotBeBlank'),
        },
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

        verbose_name = _('Label')
        verbose_name_plural = _('Labels')
        ordering = ['name']
