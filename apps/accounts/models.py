from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ORGANIZER = "ORGANIZER", "Event Organizer"
        VENDOR = "VENDOR", "Vendor / Artisan"
        PERFORMER = "PERFORMER", "Gig Worker / Performer"
        ATTENDEE = "ATTENDEE", "General Attendee"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ATTENDEE,
    )
    contact_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"