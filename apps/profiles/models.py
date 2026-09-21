from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
  """Extra, editable identity info layered on top of apps.accounts.User."""

  DISTRICT_CHOICES = [
      ("cebu_city", "Cebu City"),
      ("mandaue", "Mandaue City"),
      ("lapu_lapu", "Lapu-Lapu City"),
      ("talisay", "Talisay City"),
  ]

  user = models.OneToOneField(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name="profile",
  )
  full_name = models.CharField(max_length=150, blank=True)
  business_or_stage_name = models.CharField(
      max_length=100, blank=True, default=""
  )
  district = models.CharField(
      max_length=30, choices=DISTRICT_CHOICES, default="cebu_city"
  )
  contact_number = models.CharField(max_length=20, blank=True, default="+63")
  bio = models.TextField(blank=True, default="")
  profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

  def __str__(self):
    return f"Profile for {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_user_profile(sender, instance, created, **kwargs):
  """Ensures every new or updated user has an associated profile record in Supabase."""
  if created:
    Profile.objects.create(user=instance)
  else:
    if hasattr(instance, "profile"):
      instance.profile.save()