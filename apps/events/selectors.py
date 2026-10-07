"""Read helpers shared by the events pages and the home page."""
from django.db.models import Sum
from django.utils import timezone

from .constants import EVENT_PUBLISHED, RSVP_GOING
from .models import RSVP, Event


def upcoming_published(now=None):
    """Published events that have not ended yet, soonest first."""
    now = now or timezone.now()
    return (
        Event.objects.filter(status=EVENT_PUBLISHED, end_at__gte=now)
        .select_related("venue__district")
        .prefetch_related("categories")
        .order_by("start_at")
    )


def attach_going_counts(events):
    """Set `going_count` (sum of party sizes) on each event in one query."""
    ids = [e.pk for e in events]
    totals = dict(
        RSVP.objects.filter(event_id__in=ids, status=RSVP_GOING)
        .values("event_id")
        .annotate(total=Sum("party_size"))
        .values_list("event_id", "total")
    )
    for event in events:
        event.going_count = totals.get(event.pk, 0)
