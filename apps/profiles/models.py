from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import District


class Profile(models.Model):
    """Extra, editable identity info layered on top of apps.accounts.User.

    Sole owner of contact_number, business_or_stage_name and portfolio_url
    so they're entered once and reused everywhere (application forms read
    from here instead of asking a vendor/performer to retype them).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    business_or_stage_name = models.CharField(
        max_length=100, blank=True, default=""
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="profiles",
    )
    contact_number = models.CharField(max_length=20, blank=True, default="+63")
    bio = models.TextField(blank=True, default="")
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    portfolio_url = models.URLField(
        max_length=200, blank=True, default="",
        help_text="Default link reused on booth and gig applications.",
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Ensures every new or updated user has an associated profile record.

    District is now a required FK, so on first creation we attach a
    sensible default (Cebu City) rather than leaving it null.
    """
    if created:
        default_district, _ = District.objects.get_or_create(
            slug="cebu_city",
            defaults={"name": "Cebu City"},
        )
        Profile.objects.create(user=instance, district=default_district)
    elif hasattr(instance, "profile"):
        instance.profile.save()