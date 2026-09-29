from django.conf import settings
from django.db import models

from apps.events.models import Event


class GigRole(models.Model):
    """An open short-term role attached to an event (acoustic act,
    photographer, setup crew, ticketing marshal, ...).
    """

    class RoleType(models.TextChoices):
        ENTERTAINMENT = "ENTERTAINMENT", "Live entertainment"
        MEDIA = "MEDIA", "Media coverage"
        OPERATIONS = "OPERATIONS", "Operations"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="gig_roles"
    )
    title = models.CharField(max_length=120)
    role_type = models.CharField(max_length=15, choices=RoleType.choices)
    description = models.TextField(blank=True, default="")
    slots_total = models.PositiveSmallIntegerField(default=1)
    pay_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    call_time = models.DateTimeField(null=True, blank=True)
    apply_by = models.DateField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gig Role"
        verbose_name_plural = "Gig Roles"
        ordering = ["event", "apply_by"]
        indexes = [models.Index(fields=["is_open"])]

    def __str__(self):
        return f"{self.event.title} \u2013 {self.title}"


class GigApplication(models.Model):
    """A performer or freelancer's application for a gig role.
    portfolio_url is intentionally absent: it's read from the
    applicant's profiles_profile instead of being retyped per application.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    gig_role = models.ForeignKey(
        GigRole, on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gig_applications",
    )
    rate_amount = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    cover_note = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Gig Application"
        verbose_name_plural = "Gig Applications"
        unique_together = ("gig_role", "applicant")
        indexes = [models.Index(fields=["status"])]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.applicant.username} -> {self.gig_role.title}"