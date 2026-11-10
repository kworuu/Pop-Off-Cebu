from django.conf import settings
from django.db import models

from apps.core.models import District


class Venue(models.Model):
    """A physical location. Reused across events so districts and
    addresses stay consistent instead of being retyped per event.
    """

    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    barangay = models.CharField(
        max_length=100, help_text="Drives the Barangay Clearance requirement."
    )
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name="venues"
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        verbose_name = "Venue"
        verbose_name_plural = "Venues"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """Event theme used by discovery filters (vintage thrifting, indie
    music, artisanal food, visual arts, ...).
    """

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    """The pop-up event listing. Its venue, attendance and activity flags
    feed the automated permit checklist (see the permits app).
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    venue = models.ForeignKey(
        Venue, on_delete=models.PROTECT, related_name="events"
    )
    categories = models.ManyToManyField(
        Category,
        through="EventCategory",
        related_name="events",
        blank=True,
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True, default="")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    expected_attendance = models.PositiveIntegerField(
        default=0, help_text="Permit trigger."
    )
    is_ticketed = models.BooleanField(
        default=False, help_text="Permit trigger (Special Mayor's Permit)."
    )
    admission_fee = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Null means free entry.",
    )
    has_food_stalls = models.BooleanField(
        default=False, help_text="Permit trigger (City Health)."
    )
    involves_road_closure = models.BooleanField(
        default=False, help_text="Permit trigger (CCTO)."
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT
    )
    cover_image = models.ImageField(
        upload_to="events/covers/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-start_at"]
        indexes = [
            models.Index(fields=["start_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title


class EventCategory(models.Model):
    """Explicit through table resolving the Event <-> Category
    many-to-many. Declared explicitly (rather than a plain
    ManyToManyField) so its table name matches the approved ERD exactly.
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = "events_event_categories"
        unique_together = ("event", "category")
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return f"{self.event.title} \u2013 {self.category.name}"


class ItineraryItem(models.Model):
    """One line of an event's public schedule."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="itinerary_items"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Itinerary Item"
        verbose_name_plural = "Itinerary Items"
        ordering = ["event", "sort_order", "start_time"]

    def __str__(self):
        return f"{self.event.title}: {self.title}"


class Announcement(models.Model):
    """Logistics update the organizer posts to everyone attached to an
    event. Author uses PROTECT: a public announcement should not vanish
    or silently orphan if the author's account is later deleted.
    """

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="announcements"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="announcements_authored",
    )
    subject = models.CharField(max_length=150)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject


class RSVP(models.Model):
    """An attendee's response to an event: going, interested, or saved
    for later. GOING/INTERESTED feed the organizer's foot-traffic
    forecast; SAVED is a private bookmark.
    """

    class Status(models.TextChoices):
        GOING = "GOING", "Going"
        INTERESTED = "INTERESTED", "Interested"
        SAVED = "SAVED", "Saved"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="rsvps"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rsvps"
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.INTERESTED
    )
    party_size = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "RSVP"
        verbose_name_plural = "RSVPs"
        unique_together = ("event", "user")
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.user.username} \u2013 {self.event.title} ({self.status})"