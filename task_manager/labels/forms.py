from django import forms
from task_manager.labels.models import Label


class LabelForm(forms.ModelForm):
    """Status form."""

    class Meta(object):
        """Meta information."""

        model = Label
        fields = ['name']
