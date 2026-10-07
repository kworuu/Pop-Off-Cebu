from datetime import datetime, time, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from apps.permits.models import EventPermit
from apps.permits.services import generate_event_permits

from .constants import (
    EVENT_PENDING, EVENT_PUBLISHED, ORGANIZER_ROLE, RSVP_CHOICES, RSVP_GOING, RSVP_INTERESTED,
)
from .forms import AnnouncementForm, EventFilterForm, EventForm, RSVPForm
from .models import RSVP, Announcement, Event, ItineraryItem
from .selectors import attach_going_counts

PAGE_SIZE = 9


# ---------------------------------------------------------------- helpers

def organizer_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.role != ORGANIZER_ROLE:
            messages.error(request, "Only event organizers can do that.")
            return redirect("events:list")
        return view(request, *args, **kwargs)

    return login_required(wrapper)


def _unique_slug(title):
    base = slugify(title)[:200] or "event"
    slug, n = base, 2
    while Event.objects.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def _day_bounds(day):
    start = timezone.make_aware(datetime.combine(day, time.min))
    return start, start + timedelta(days=1)


def _weekend_bounds(today):
    """Saturday 00:00 to Monday 00:00 of the current (or next) weekend."""
    offset = today.weekday() - 5  # Saturday == 5
    saturday = today - timedelta(days=offset) if offset >= 0 else today + timedelta(days=-offset)
    start = timezone.make_aware(datetime.combine(saturday, time.min))
    return start, start + timedelta(days=2)


def _apply_when(qs, cleaned, now):
    day = cleaned.get("date")
    when = cleaned.get("when") or "upcoming"
    if day:
        start, end = _day_bounds(day)
    elif when == "today":
        start, end = _day_bounds(timezone.localdate())
    elif when == "weekend":
        start, end = _weekend_bounds(timezone.localdate())
    else:
        return qs.filter(end_at__gte=now)
    floor = start if day else max(start, now)
    return qs.filter(start_at__lt=end, end_at__gte=floor)


# ------------------------------------------------------------- public views

def event_list(request):
    form = EventFilterForm(request.GET or None)
    cleaned = form.cleaned_data if form.is_valid() else {}
    now = timezone.now()

    qs = (
        Event.objects.filter(status=EVENT_PUBLISHED)
        .select_related("venue__district")
        .prefetch_related("categories")
    )
    if cleaned.get("q"):
        q = cleaned["q"]
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
            | Q(venue__name__icontains=q) | Q(venue__barangay__icontains=q)
        )
    if cleaned.get("district"):
        qs = qs.filter(venue__district=cleaned["district"])
    if cleaned.get("category"):
        qs = qs.filter(categories=cleaned["category"])
    qs = _apply_when(qs, cleaned, now).order_by("start_at")

    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    attach_going_counts(page.object_list)

    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "events/event_list.html", {
        "form": form,
        "page": page,
        "querystring": params.urlencode(),
        "filters_active": bool(params),
    })


def event_detail(request, slug):
    event = get_object_or_404(
        Event.objects.select_related("venue__district", "organizer"), slug=slug
    )
    user = request.user
    is_owner = user.is_authenticated and event.organizer_id == user.id
    if event.status != EVENT_PUBLISHED and not (is_owner or user.is_staff):
        raise Http404

    now = timezone.now()
    going = RSVP.objects.filter(event=event, status=RSVP_GOING).aggregate(t=Sum("party_size"))["t"] or 0
    interested = RSVP.objects.filter(event=event, status=RSVP_INTERESTED).count()
    context = {
        "event": event,
        "categories": event.categories.all(),
        "itinerary": ItineraryItem.objects.filter(event=event).order_by("sort_order", "start_time"),
        "announcements": Announcement.objects.filter(event=event)
        .select_related("author").order_by("-created_at"),
        "going_count": going,
        "interested_count": interested,
        "user_rsvp": RSVP.objects.filter(event=event, user=user).first() if user.is_authenticated else None,
        "can_rsvp": event.status == EVENT_PUBLISHED and event.end_at >= now,
        "is_past": event.end_at < now,
        "is_owner": is_owner,
        "rsvp_choices": RSVP_CHOICES,
    }
    if is_owner:
        context["permits"] = (
            EventPermit.objects.filter(event=event)
            .select_related("permit_type").order_by("permit_type__name")
        )
        context["announcement_form"] = AnnouncementForm()
    return render(request, "events/event_detail.html", context)


@login_required
@require_POST
def rsvp(request, slug):
    event = get_object_or_404(Event, slug=slug, status=EVENT_PUBLISHED)
    if event.end_at < timezone.now():
        messages.error(request, "This event has already ended.")
        return redirect("events:detail", slug=slug)

    if request.POST.get("action") == "cancel":
        RSVP.objects.filter(event=event, user=request.user).delete()
        messages.success(request, "RSVP removed.")
        return redirect("events:detail", slug=slug)

    form = RSVPForm(request.POST)
    if form.is_valid():
        RSVP.objects.update_or_create(
            event=event, user=request.user,
            defaults={"status": form.cleaned_data["status"],
                      "party_size": form.cleaned_data["party_size"]},
        )
        messages.success(request, "RSVP saved.")
    else:
        messages.error(request, "Choose an RSVP option and a party size from 1 to 20.")
    return redirect("events:detail", slug=slug)


# ---------------------------------------------------------- organizer views

@transaction.atomic
def _persist_event(form, organizer, creating):
    event = form.save(commit=False)
    event.venue = form.resolve_venue()
    if creating:
        event.organizer = organizer
        event.slug = _unique_slug(event.title)
        event.status = EVENT_PENDING
    event.save()
    form.save_m2m()
    created_permits = generate_event_permits(event)
    return event, created_permits


@organizer_required
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event, permits = _persist_event(form, request.user, creating=True)
        messages.success(
            request,
            f"Event submitted for review. We added {len(permits)} items to your permit checklist.",
        )
        return redirect("events:detail", slug=event.slug)
    return render(request, "events/event_form.html", {"form": form, "event": None})


@organizer_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        event, permits = _persist_event(form, request.user, creating=False)
        extra = f" {len(permits)} new permit items were added." if permits else ""
        messages.success(request, f"Event updated.{extra}")
        return redirect("events:detail", slug=event.slug)
    return render(request, "events/event_form.html", {"form": form, "event": event})


@organizer_required
def my_events(request):
    events = list(
        Event.objects.filter(organizer=request.user)
        .select_related("venue__district").order_by("-start_at")
    )
    attach_going_counts(events)
    permit_totals = dict(
        EventPermit.objects.filter(event__in=events)
        .values("event_id").annotate(n=Count("id")).values_list("event_id", "n")
    )
    for event in events:
        event.permit_count = permit_totals.get(event.pk, 0)
    return render(request, "events/my_events.html", {"events": events})


@organizer_required
@require_POST
def post_announcement(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    form = AnnouncementForm(request.POST)
    if form.is_valid():
        announcement = form.save(commit=False)
        announcement.event = event
        announcement.author = request.user
        announcement.save()
        messages.success(request, "Announcement posted.")
    else:
        messages.error(request, "Add a subject and a message before posting.")
    return redirect("events:detail", slug=slug)
