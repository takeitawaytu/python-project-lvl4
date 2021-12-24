from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from task_manager.labels.models import Label
from task_manager.statuses.models import Status


class Tasks(models.Model):
    """Tasks model."""

    max_name_field_length = 150
    user = get_user_model()
    name = models.CharField(
        max_length=max_name_field_length,
        unique=True,
        verbose_name=_('TasksName'),
        help_text=_('HelpTaskFieldText'),
        error_messages={
            'unique': _('TaskWithThisNameAlreadyExist'),
            'blank': _('ThisFieldCannotBeBlank'),
        },
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('TaskDescription'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(
        Status,
        related_name='statuses',
        on_delete=models.PROTECT,
        verbose_name=_('Status'),
    )
    executor = models.ForeignKey(
        user,
        related_name='executors',
        on_delete=models.PROTECT,
        verbose_name=_('TaskExecutor'),
        blank=True,
        null=True,
    )
    creator = models.ForeignKey(
        user,
        related_name='creators',
        on_delete=models.PROTECT,
        verbose_name=_('TaskCreator'),
    )
    labels = models.ManyToManyField(
        Label,
        related_name='labels',
        through='TaskLabelRelated',
        through_fields=('task', 'label'),
        verbose_name=_('Labels'),
        blank=True,
    )

    def __str__(self) -> str:
        """
        String representation.
        Returns:
            str:
        """
        return self.name

    class Meta(object):
        """Meta information."""

        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-created_at']


class TaskLabelRelated(models.Model):
    """Task-Label related model."""

    task = models.ForeignKey(
        Tasks,
        related_name='task',
        on_delete=models.CASCADE,
    )
    label = models.ForeignKey(
        Label,
        related_name='label',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
