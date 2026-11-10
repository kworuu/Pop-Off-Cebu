from django.shortcuts import render
from django.urls import reverse

from apps.events.constants import ORGANIZER_ROLE
from apps.events.selectors import attach_going_counts, upcoming_published

LANES = [
    ("01", "ORGANIZER", "Organizer",
     "Open a pop-up, get a permit checklist for your venue, and fill every stall and stage slot.",
     "Host an event"),
    ("02", "VENDOR", "Vendor",
     "Find a stall near the crowd, see the fees up front, and track your application.",
     "Reserve a stall"),
    ("03", "PERFORMER", "Performer",
     "Book sets and crew gigs, share your portfolio, and build a name across the city.",
     "Find gigs"),
    ("04", "ATTENDEE", "Attendee",
     "Follow your favorite makers, save events, and tell your barkada you're going.",
     "Browse events"),
]


def _lane_url(user, role):
    """Where a lane button goes. Booth and gig pages arrive in later phases,
    so vendors and performers land on the events list for now."""
    if not user.is_authenticated:
        return reverse("register:register")
    if role == "ORGANIZER" and user.role == ORGANIZER_ROLE:
        return reverse("events:create")
    return reverse("events:list")


def _secondary_cta(user):
    if not user.is_authenticated:
        return {"label": "Join the community", "url": reverse("register:register")}
    if user.role == ORGANIZER_ROLE:
        return {"label": "Host an event", "url": reverse("events:create")}
    return None


def home_view(request):
    events = list(upcoming_published()[:4])
    attach_going_counts(events)
    lanes = [
        {"num": num, "title": title, "text": text, "cta": cta, "url": _lane_url(request.user, code)}
        for num, code, title, text, cta in LANES
    ]
    return render(request, "home/home.html", {
        "next_up": events[0] if events else None,
        "coming": events[1:],
        "lanes": lanes,
        "secondary_cta": _secondary_cta(request.user),
    })
