from typing import Any

import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from task_manager.labels.models import Label
from task_manager.tasks.models import Tasks


class TasksFilter(django_filters.FilterSet):
    """Tasks filter."""

    label = django_filters.ModelChoiceFilter(
        field_name='labels',
        label=_('FilterLabels'),
        queryset=Label.objects.all(),
    )
    self_tasks = django_filters.BooleanFilter(
        field_name='creator',
        label=_('FilterOnlyCreatorTasks'),
        method='creator_tasks_filter',
        widget=forms.CheckboxInput,
    )

    def creator_tasks_filter(self, queryset, name, value) -> Any:
        """
        Custom filter. Get task where auth_user is creator.
        Args:
            queryset:
            name:
            value:
        Returns:
            Any:
        """

        if value:
            return queryset.filter(creator=self.request.user)
        return queryset

    class Meta(object):
        """Meta information."""

        model = Tasks
        fields = ['status', 'executor']
