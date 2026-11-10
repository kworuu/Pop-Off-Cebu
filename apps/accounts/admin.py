from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountUserAdmin(UserAdmin):
    """Adds the Pop-off Cebu role field to the stock Django UserAdmin.
    contact_number was removed: it now lives only on profiles_profile.
    """

    fieldsets = UserAdmin.fieldsets + (
        ("Pop-off Cebu profile", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff")
    list_filter = UserAdmin.list_filter + ("role",)