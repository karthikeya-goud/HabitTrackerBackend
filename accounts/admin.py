from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "tpass",
        "is_staff",
    )
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")

    ordering = ("id",)

    fieldsets = BaseUserAdmin.fieldsets + (("Extra Info", {"fields": ("created_at",)}),)

    readonly_fields = ("created_at",)


admin.site.register(User, UserAdmin)
