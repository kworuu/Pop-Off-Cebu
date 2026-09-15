from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountUserAdmin(UserAdmin):
    """Adds the Pop-off Cebu role/contact fields to the stock Django UserAdmin."""

    fieldsets = UserAdmin.fieldsets + (
        ("Pop-off Cebu profile", {"fields": ("role", "contact_number")}),
    )
    list_display = ("username", "email", "role", "is_staff")
    list_filter = UserAdmin.list_filter + ("role",)
