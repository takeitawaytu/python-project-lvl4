from django.contrib import admin
from task_manager.labels.models import Label


class LabelsAdmin(admin.ModelAdmin):
    """Label model in admins."""

    list_display = ('id', 'name', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)


admin.site.register(Label, LabelsAdmin)
