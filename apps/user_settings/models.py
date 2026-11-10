from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    """Per-user preferences, created on first visit to Settings.

    public_profile was added here: the settings view and template already
    read/write it, but it was missing from the original model, which would
    have raised an error on save.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"