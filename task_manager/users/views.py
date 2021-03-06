from typing import Any, Dict, Union

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from django.http.response import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.tasks.models import Tasks
from task_manager.users.forms import CustomUserCreationForm
from task_manager.users.mixins import CheckUserRightsTestMixin


class UserListView(ListView):
    """User listing."""

    model = get_user_model()
    paginate_by = 10
    context_object_name = 'users_list'
    template_name = 'users/index.html'


class UserDetailView(CheckUserRightsTestMixin, DetailView):
    """User detail view."""

    model = get_user_model()
    context_object_name = 'user'
    login_url = reverse_lazy('login')
    template_name = 'users/detail.html'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Insert the single object into the context dict.
        Returns:
            Dict:
        """
        context = super().get_context_data(**kwargs)
        context['count_tasks_by_user'] = Tasks.objects.filter(
            creator=self.request.user.id,
        ).count()
        context['count_tasks_to_user'] = Tasks.objects.filter(
            executor=self.request.user.id,
        ).count()
        return context


class UserCreateView(SuccessMessageMixin, CreateView):
    """User create."""

    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'users/create.html'
    success_message = _('SuccessCreateUser')
    success_url = reverse_lazy('login')


class UserUpdateView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """User update."""

    model = get_user_model()
    context_object_name = 'user'
    form_class = CustomUserCreationForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users')
    success_message = _('SuccessUpdateUser')
    redirect_url = reverse_lazy('users')


class UserDeleteView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """User delete."""

    model = get_user_model()
    context_object_name = 'user'
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users')
    success_message = _('SuccessDeleteUser')
    redirect_url = reverse_lazy('users')

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
            messages.error(self.request, _('CannotDeleteUser'))
            return redirect('users')


class UserLoginView(SuccessMessageMixin, LoginView):
    """User login."""

    template_name = 'users/login.html'
    success_message = _('SuccessLoginUser')
    redirect_url = reverse_lazy('home')


class UserLogoutView(LogoutView):
    """User logout."""

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.
        Args:
            request:
        Returns:
            Any:
        """
        if request.user.is_authenticated:
            messages.success(request, _('SuccessLogoutUser'))
        return super().dispatch(request, *args, **kwargs)
