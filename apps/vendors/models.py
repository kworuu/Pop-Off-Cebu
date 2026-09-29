from django.conf import settings
from django.db import models

from apps.events.models import Event
from apps.permits.models import PermitType


class BoothTier(models.Model):
    """A booth category an organizer opens for applications on a given
    event, with dimension limits, power allocation and fee.
    """

    class BoothCategory(models.TextChoices):
        DRY_GOODS = "DRY_GOODS", "Dry goods / crafts"
        HOT_COOKING = "HOT_COOKING", "Hot cooking"
        BEVERAGE = "BEVERAGE", "Beverage station"
        ART_INSTALL = "ART_INSTALL", "Interactive art installation"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="booth_tiers"
    )
    required_permits = models.ManyToManyField(
        PermitType,
        through="permits.BoothTierRequirement",
        related_name="booth_tiers",
        blank=True,
    )
    name = models.CharField(max_length=100)
    booth_category = models.CharField(
        max_length=20, choices=BoothCategory.choices
    )
    max_width_m = models.DecimalField(max_digits=5, decimal_places=2)
    max_depth_m = models.DecimalField(max_digits=5, decimal_places=2)
    power_watts = models.PositiveIntegerField(
        default=0, help_text="0 means no power provided."
    )
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    slots_total = models.PositiveSmallIntegerField(default=1)
    guidelines = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Booth Tier"
        verbose_name_plural = "Booth Tiers"
        ordering = ["event", "name"]

    def __str__(self):
        return f"{self.event.title} \u2013 {self.name}"


class BoothApplication(models.Model):
    """A vendor's application for a booth tier. business_name and
    portfolio_url are intentionally absent here: they're read from the
    vendor's profiles_profile instead of being retyped per application.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    booth_tier = models.ForeignKey(
        BoothTier, on_delete=models.CASCADE, related_name="applications"
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="booth_applications",
    )
    product_description = models.TextField(help_text="Menu or product range.")
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    organizer_notes = models.TextField(blank=True, default="")
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Booth Application"
        verbose_name_plural = "Booth Applications"
        unique_together = ("booth_tier", "vendor")
        indexes = [models.Index(fields=["status"])]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.vendor.username} -> {self.booth_tier.name}"