from django.contrib import admin
from task_manager.tasks.models import Tasks


class TasksAdmin(admin.ModelAdmin):
    """Task model in admins."""

    list_display = (
        'name',
        'description',
        'executor',
        'creator',
        'status',
        'created_at',
    )
    list_display_links = ('name', )
    search_fields = ('name', 'executor', 'creator', 'status')
    list_filter = ('executor', 'creator', 'status')


admin.site.register(Tasks, TasksAdmin)
