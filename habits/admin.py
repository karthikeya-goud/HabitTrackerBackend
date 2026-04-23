from django.contrib import admin

# Register your models here.
from .models import Task, TaskLog, Logs


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "priority",
        "type",
        "frequency",
        "is_active",
        "is_soft_deleted",
        "is_deleted",
    )
    list_filter = ("type", "frequency", "is_active", "is_soft_deleted", "is_deleted")
    search_fields = ("title", "description")
    ordering = (
        "id",
        "priority",
    )

    # Show only user's tasks (unless superuser)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # Auto-assign user on create
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # only when creating
            obj.user = request.user
        super().save_model(request, obj, form, change)


class TaskLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "task",
        "value",
        "target_value",
        "unit",
        "type",
        "completion_percentage",
        "score_earned",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("task__title", "user__username")
    ordering = ("-created_at",)

    # Restrict logs per user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # Prevent editing logs (optional but recommended)
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(Logs)
