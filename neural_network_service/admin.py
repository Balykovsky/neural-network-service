from django.contrib import admin
from neural_network_service.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('huey_id', 'status', 'started_at',
                    'finished_at', 'error')
    list_filter = ('started_at', 'finished_at')


admin.site.register(Task, TaskAdmin)