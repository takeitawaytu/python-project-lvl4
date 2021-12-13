from django.urls import path

from task_manager.users.views import (
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserUpdateView,
)


urlpatterns = [
    path('', UserListView.as_view(), name='users'),
    path('create/', UserCreateView.as_view(), name='create_user'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='update_user'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='delete_user'),
]
