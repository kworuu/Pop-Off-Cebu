"""
Compliance engine, step 1: turn an event's flags into a permit checklist.

Each PermitType row carries a `trigger_rule` code. This module maps each
code to a predicate over the event. Adding a new rule means adding one
entry to TRIGGER_RULES and one PermitType row; no view code changes.

generate_event_permits() is additive and idempotent. It never deletes or
downgrades an EventPermit, because an organizer may already have filed
paperwork for a permit that a later edit made "unnecessary".
"""
import logging

from .constants import PERMIT_SCOPE_EVENT
from .models import EventPermit, PermitType

logger = logging.getLogger(__name__)

TRIGGER_RULES = {
    "ALWAYS": lambda e: True,
    "HAS_FOOD": lambda e: bool(e.has_food_stalls),
    "ROAD_CLOSURE": lambda e: bool(e.involves_road_closure),
    "TICKETED": lambda e: bool(e.is_ticketed),
    "CROWD_100": lambda e: (e.expected_attendance or 0) >= 100,
    "CROWD_500": lambda e: (e.expected_attendance or 0) > 500,
}


def required_permit_types(event):
    """PermitType rows (event scope) whose trigger matches this event."""
    matched = []
    for permit_type in PermitType.objects.filter(scope=PERMIT_SCOPE_EVENT).order_by("name"):
        rule = TRIGGER_RULES.get(permit_type.trigger_rule)
        if rule is None:
            logger.warning(
                "PermitType %s has unknown trigger_rule %r; skipped.",
                permit_type.code,
                permit_type.trigger_rule,
            )
            continue
        if rule(event):
            matched.append(permit_type)
    return matched


def generate_event_permits(event):
    """Create any missing EventPermit rows. Returns the newly created ones."""
    created = []
    for permit_type in required_permit_types(event):
        obj, was_created = EventPermit.objects.get_or_create(
            event=event, permit_type=permit_type
        )
        if was_created:
            created.append(obj)
    return created
