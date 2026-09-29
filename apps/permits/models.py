from django.conf import settings
from django.db import models

from apps.events.models import Event


class PermitType(models.Model):
    """Catalogue of permits and clearances. trigger_rule is what the
    checklist generator evaluates against an event's flags.
    """

    class Scope(models.TextChoices):
        EVENT = "EVENT", "Event-level"
        VENDOR = "VENDOR", "Vendor-level"

    class TriggerRule(models.TextChoices):
        ALWAYS = "ALWAYS", "Always required"
        HAS_FOOD = "HAS_FOOD", "Required when the event has food stalls"
        ROAD_CLOSURE = "ROAD_CLOSURE", "Required when the event closes roads"
        TICKETED = "TICKETED", "Required when the event is ticketed"

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    issuing_office = models.CharField(max_length=150)
    scope = models.CharField(max_length=10, choices=Scope.choices)
    trigger_rule = models.CharField(
        max_length=30, choices=TriggerRule.choices, default=TriggerRule.ALWAYS
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Permit Type"
        verbose_name_plural = "Permit Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EventPermit(models.Model):
    """An organizer's generated checklist: one row per permit an event
    needs. permit_type uses PROTECT so the catalogue entry can't be
    deleted out from under an event that references it.
    """

    class Status(models.TextChoices):
        REQUIRED = "REQUIRED", "Required"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="permits"
    )
    permit_type = models.ForeignKey(
        PermitType, on_delete=models.PROTECT, related_name="event_permits"
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.REQUIRED
    )
    reference_no = models.CharField(max_length=60, blank=True, default="")
    document = models.FileField(
        upload_to="permits/events/", blank=True, null=True
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Event Permit"
        verbose_name_plural = "Event Permits"
        unique_together = ("event", "permit_type")
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.event.title} \u2013 {self.permit_type.name}"


class VendorCompliance(models.Model):
    """Documents a vendor already holds (health card, DTI/BMBE,
    fire-safety clearance) ahead of applying for a booth tier.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        EXPIRED = "EXPIRED", "Expired"

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="compliance_documents",
    )
    permit_type = models.ForeignKey(
        PermitType, on_delete=models.PROTECT, related_name="vendor_compliance_records"
    )
    reference_no = models.CharField(max_length=60, blank=True, default="")
    document = models.FileField(
        upload_to="permits/vendors/", blank=True, null=True
    )
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        verbose_name = "Vendor Compliance"
        verbose_name_plural = "Vendor Compliance Records"
        unique_together = ("vendor", "permit_type")

    def __str__(self):
        return f"{self.vendor.username} \u2013 {self.permit_type.name}"


class BoothTierRequirement(models.Model):
    """Explicit through table: which vendor-side permits a booth tier
    demands. booth_tier references 'vendors.BoothTier' as a string to
    avoid a circular import between the permits and vendors apps.
    """

    booth_tier = models.ForeignKey(
        "vendors.BoothTier",
        on_delete=models.CASCADE,
        related_name="tier_requirements",
    )
    permit_type = models.ForeignKey(
        PermitType, on_delete=models.PROTECT, related_name="tier_requirements"
    )

    class Meta:
        db_table = "permits_boothtierrequirement"
        unique_together = ("booth_tier", "permit_type")
        verbose_name = "Booth Tier Requirement"
        verbose_name_plural = "Booth Tier Requirements"

    def __str__(self):
        return f"{self.booth_tier.name} requires {self.permit_type.name}"