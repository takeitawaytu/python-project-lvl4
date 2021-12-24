from typing import Any, Union

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from task_manager.tasks.filters import TasksFilter
from task_manager.tasks.forms import TasksForm
from task_manager.tasks.mixins import (
    CheckUserRightsTestMixin,
    CustomLoginRequiredMixin,
)
from task_manager.tasks.models import Tasks


class TaskListView(CustomLoginRequiredMixin, FilterView):
    """Task listing."""

    model = Tasks
    paginate_by = 10
    login_url = reverse_lazy('login')
    context_object_name = 'tasks_list'
    template_name = 'tasks/index.html'
    filterset_class = TasksFilter


class TaskDetailView(CustomLoginRequiredMixin, DetailView):
    """Task detail view."""

    model = Tasks
    context_object_name = 'task'
    login_url = reverse_lazy('login')
    template_name = 'tasks/detail.html'


class TaskCreateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Task create."""

    model = Tasks
    form_class = TasksForm
    login_url = reverse_lazy('login')
    template_name = 'tasks/create.html'
    success_message = _('SuccessCreateTask')
    success_url = reverse_lazy('tasks')

    def form_valid(self, form) -> Any:
        """
        If the form is valid, save the associated model.
        Args:
            form:
        Returns:
            Any:
        """
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Task update."""

    model = Tasks
    context_object_name = 'task'
    form_class = TasksForm
    login_url = reverse_lazy('login')
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks')
    success_message = _('SuccessUpdateTask')


class TaskDeleteView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """Task delete."""

    model = Tasks
    context_object_name = 'task'
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks')
    success_message = _('SuccessDeleteTask')
    redirect_url = reverse_lazy('tasks')

    def test_func(self) -> bool:
        """
        Test function.
        Returns:
            bool:
        """
        return self.get_object().creator == self.request.user

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
        response = self.delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return response
