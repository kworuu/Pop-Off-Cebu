from django.db import models


class District(models.Model):
    """Lookup table for Metro Cebu districts.

    Shared by profiles_profile and events_venue so the list of valid
    districts is maintained in exactly one place instead of being
    hardcoded as choices on multiple models.
    """

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ["name"]

    def __str__(self):
        return self.name