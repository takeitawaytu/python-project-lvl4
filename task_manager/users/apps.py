from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Config user."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager.users'
