from django.contrib import admin
from task_manager.statuses.models import Status


class StatusesAdmin(admin.ModelAdmin):
    """Status model in admins."""

    list_display = ('id', 'name', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Status, StatusesAdmin)
