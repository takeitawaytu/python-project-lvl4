from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.statuses.forms import StatusForm
from task_manager.statuses.mixins import CustomLoginRequiredMixin
from task_manager.statuses.models import Status


class StatusListView(CustomLoginRequiredMixin, ListView):
    """Status listing."""

    model = Status
    paginate_by = 10
    login_url = reverse_lazy('login')
    context_object_name = 'statuses_list'
    template_name = 'statuses/index.html'


class StatusCreateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Status create."""

    model = Status
    form_class = StatusForm
    login_url = reverse_lazy('login')
    template_name = 'statuses/create.html'
    success_message = _('SuccessCreateStatus')
    success_url = reverse_lazy('statuses')


class StatusUpdateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Status update."""

    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses')
    success_message = _('SuccessUpdateStatus')


class StatusDeleteView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """Status delete."""

    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses')
    success_message = _('SuccessDeleteStatus')
