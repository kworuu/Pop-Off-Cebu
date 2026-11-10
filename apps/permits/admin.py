from django.contrib import admin

from .models import EventPermit, PermitType


@admin.register(PermitType)
class PermitTypeAdmin(admin.ModelAdmin):
    """Admins keep LGU rules current here (spec: 'Update LGU Statutes')."""

    list_display = ("name", "code", "scope", "trigger_rule", "issuing_office")
    list_filter = ("scope",)
    search_fields = ("name", "code", "issuing_office")


@admin.register(EventPermit)
class EventPermitAdmin(admin.ModelAdmin):
    list_display = ("event", "permit_type", "status", "reference_no")
    list_filter = ("status", "permit_type")
