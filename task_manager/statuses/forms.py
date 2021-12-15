from django import forms
from task_manager.statuses.models import Status


class StatusForm(forms.ModelForm):
    """Status form."""

    class Meta(object):
        """Meta information."""

        model = Status
        fields = ['name']
