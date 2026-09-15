from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra, editable identity info layered on top of apps.accounts.User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
