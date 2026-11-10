from django.contrib import admin

from .constants import EVENT_PENDING, EVENT_PUBLISHED
from .models import Category, Event, ItineraryItem, Venue


class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Moderation queue: filter by status, then use the Publish action."""

    list_display = ("title", "organizer", "venue", "start_at", "status")
    list_filter = ("status", "venue__district")
    search_fields = ("title", "organizer__username")
    date_hierarchy = "start_at"
    inlines = [ItineraryItemInline]
    actions = ["publish_events"]

    @admin.action(description="Publish selected events (pending review only)")
    def publish_events(self, request, queryset):
        n = queryset.filter(status=EVENT_PENDING).update(status=EVENT_PUBLISHED)
        self.message_user(request, f"Published {n} event(s).")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "barangay", "district")
    list_filter = ("district",)
    search_fields = ("name", "address", "barangay")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
