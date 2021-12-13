from django.contrib import admin
from django.contrib.auth import get_user_model


class CustomUsersAdmin(admin.ModelAdmin):
    """User model in admins."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'is_superuser',
    )
    list_display_links = ('id', 'username')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('first_name', 'last_name')


admin.site.register(get_user_model(), CustomUsersAdmin)
