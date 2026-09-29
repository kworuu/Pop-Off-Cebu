from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. The role decides which dashboard and actions a
    person gets. contact_number was removed from here: profiles_profile
    is now the single source of truth for that value (see the profiles
    app), so it never has to be kept in sync across two tables.
    """

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

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"