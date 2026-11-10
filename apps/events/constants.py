"""
String values this slice assumes exist in models.py.

If your models use different choice values, change them here and
nothing else needs to move.
"""

ORGANIZER_ROLE = "ORGANIZER"

EVENT_PENDING = "DRAFT"  # model has no PENDING_REVIEW; DRAFT == awaiting admin review
EVENT_PUBLISHED = "PUBLISHED"
EVENT_CANCELLED = "CANCELLED"

RSVP_GOING = "GOING"
RSVP_INTERESTED = "INTERESTED"
RSVP_SAVED = "SAVED"
RSVP_CHOICES = [
    (RSVP_GOING, "Going"),
    (RSVP_INTERESTED, "Interested"),
    (RSVP_SAVED, "Saved for later"),
]
