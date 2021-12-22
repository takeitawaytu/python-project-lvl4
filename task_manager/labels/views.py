from typing import Union

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from django.http.response import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.labels.forms import LabelForm
from task_manager.labels.models import Label
from task_manager.mixins import CustomLoginRequiredMixin


class LabelListView(CustomLoginRequiredMixin, ListView):
    """Label listing."""

    model = Label
    paginate_by = 10
    login_url = reverse_lazy('login')
    context_object_name = 'labels_list'
    template_name = 'labels/index.html'


class LabelCreateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Label create."""

    model = Label
    form_class = LabelForm
    login_url = reverse_lazy('login')
    template_name = 'labels/create.html'
    success_message = _('SuccessCreateLabel')
    success_url = reverse_lazy('labels')


class LabelUpdateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Label update."""

    model = Label
    context_object_name = 'label'
    form_class = LabelForm
    template_name = 'labels/update.html'
    success_url = reverse_lazy('labels')
    success_message = _('SuccessUpdateLabel')


class LabelDeleteView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """Label delete."""

    model = Label
    context_object_name = 'label'
    template_name = 'labels/delete.html'
    success_url = reverse_lazy('labels')
    success_message = _('SuccessDeleteLabel')

    def post(self, request, *args, **kwargs) -> Union[
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    ]:
        """
        Override 'post' in DeletionMixin.
        Args:
            request: request
        Returns:
            Union:
        """
        try:
            response = self.delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return response
        except ProtectedError:
            messages.error(self.request, _('CannotDeleteLabel'))
            return redirect('labels')
