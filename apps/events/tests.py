from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import District
from apps.permits.models import EventPermit, PermitType
from apps.permits.services import generate_event_permits

from .constants import EVENT_PENDING, EVENT_PUBLISHED, RSVP_GOING
from .models import RSVP, Category, Event, Venue

User = get_user_model()


def make_event(organizer, venue, **overrides):
    now = timezone.now()
    fields = dict(
        organizer=organizer, venue=venue, title="Test event", slug="test-event",
        description="Description", start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=2, hours=4), expected_attendance=50,
        is_ticketed=False, admission_fee=None, has_food_stalls=False,
        involves_road_closure=False, status=EVENT_PUBLISHED,
    )
    fields.update(overrides)
    return Event.objects.create(**fields)


class EventTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = User.objects.create_user("org", password="pw-12345-test", role="ORGANIZER")
        cls.attendee = User.objects.create_user("att", password="pw-12345-test", role="ATTENDEE")
        cls.district, _ = District.objects.get_or_create(name="Cebu City", defaults={"slug": "cebu-city"})
        cls.venue = Venue.objects.create(
            name="Parking Lot A", address="Lahug", barangay="Lahug", district=cls.district
        )
        cls.category = Category.objects.create(name="Artisan Crafts", slug="artisan-crafts")
        PermitType.objects.create(code="ALWAYS_T", name="Always", issuing_office="Barangay",
                                  scope="EVENT", trigger_rule="ALWAYS", description="")
        PermitType.objects.create(code="FOOD_T", name="Food", issuing_office="CHD",
                                  scope="EVENT", trigger_rule="HAS_FOOD", description="")
        PermitType.objects.create(code="ROAD_T", name="Road", issuing_office="CCTO",
                                  scope="EVENT", trigger_rule="ROAD_CLOSURE", description="")


class PermitGeneratorTests(EventTestBase):
    def test_only_matching_rules_create_permits(self):
        event = make_event(self.organizer, self.venue, has_food_stalls=True)
        created = generate_event_permits(event)
        codes = {p.permit_type.code for p in created}
        self.assertEqual(codes, {"ALWAYS_T", "FOOD_T"})

    def test_generation_is_idempotent_and_never_deletes(self):
        event = make_event(self.organizer, self.venue, has_food_stalls=True)
        generate_event_permits(event)
        event.has_food_stalls = False
        event.save()
        self.assertEqual(generate_event_permits(event), [])
        self.assertEqual(EventPermit.objects.filter(event=event).count(), 2)

    def test_unknown_rule_is_skipped(self):
        PermitType.objects.create(code="ODD", name="Odd", issuing_office="X",
                                  scope="EVENT", trigger_rule="NOPE", description="")
        event = make_event(self.organizer, self.venue)
        codes = {p.permit_type.code for p in generate_event_permits(event)}
        self.assertEqual(codes, {"ALWAYS_T"})


class DiscoveryTests(EventTestBase):
    def test_list_shows_only_published_upcoming_events(self):
        make_event(self.organizer, self.venue, title="Visible", slug="visible")
        make_event(self.organizer, self.venue, title="Hidden pending", slug="pending",
                   status=EVENT_PENDING)
        past = timezone.now() - timedelta(days=3)
        make_event(self.organizer, self.venue, title="Old one", slug="old",
                   start_at=past, end_at=past + timedelta(hours=3))
        response = self.client.get(reverse("events:list"))
        titles = [e.title for e in response.context["page"].object_list]
        self.assertEqual(titles, ["Visible"])

    def test_district_filter(self):
        other, _ = District.objects.get_or_create(name="Mandaue City", defaults={"slug": "mandaue"})
        other_venue = Venue.objects.create(name="Plaza", address="X", barangay="Y", district=other)
        make_event(self.organizer, self.venue, title="Cebu one", slug="cebu-one")
        make_event(self.organizer, other_venue, title="Mandaue one", slug="mandaue-one")
        response = self.client.get(reverse("events:list"), {"district": other.slug})
        titles = [e.title for e in response.context["page"].object_list]
        self.assertEqual(titles, ["Mandaue one"])

    def test_pending_event_detail_is_hidden_from_public_but_visible_to_owner(self):
        event = make_event(self.organizer, self.venue, status=EVENT_PENDING)
        url = reverse("events:detail", args=[event.slug])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.organizer)
        self.assertEqual(self.client.get(url).status_code, 200)


class RSVPTests(EventTestBase):
    def setUp(self):
        self.event = make_event(self.organizer, self.venue)
        self.url = reverse("events:rsvp", args=[self.event.slug])

    def test_requires_login(self):
        response = self.client.post(self.url, {"status": RSVP_GOING, "party_size": 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RSVP.objects.count(), 0)

    def test_rsvp_is_updated_not_duplicated(self):
        self.client.force_login(self.attendee)
        self.client.post(self.url, {"status": RSVP_GOING, "party_size": 2})
        self.client.post(self.url, {"status": RSVP_GOING, "party_size": 4})
        self.assertEqual(RSVP.objects.filter(event=self.event).count(), 1)
        self.assertEqual(RSVP.objects.get(event=self.event).party_size, 4)

    def test_cancel_removes_rsvp(self):
        self.client.force_login(self.attendee)
        self.client.post(self.url, {"status": RSVP_GOING, "party_size": 1})
        self.client.post(self.url, {"action": "cancel"})
        self.assertEqual(RSVP.objects.count(), 0)

    def test_going_count_sums_party_size(self):
        self.client.force_login(self.attendee)
        self.client.post(self.url, {"status": RSVP_GOING, "party_size": 3})
        response = self.client.get(reverse("events:detail", args=[self.event.slug]))
        self.assertEqual(response.context["going_count"], 3)


class OrganizerFlowTests(EventTestBase):
    def payload(self, **overrides):
        data = {
            "title": "Night Market", "description": "Food and music",
            "categories": [self.category.pk], "venue": self.venue.pk,
            "start_at": "2030-12-05T10:00", "end_at": "2030-12-05T18:00",
            "expected_attendance": 150, "has_food_stalls": "on",
        }
        data.update(overrides)
        return data

    def test_attendee_cannot_create(self):
        self.client.force_login(self.attendee)
        response = self.client.post(reverse("events:create"), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_sets_pending_status_slug_and_permits(self):
        self.client.force_login(self.organizer)
        self.client.post(reverse("events:create"), self.payload())
        event = Event.objects.get(title="Night Market")
        self.assertEqual(event.status, EVENT_PENDING)
        self.assertEqual(event.slug, "night-market")
        self.assertEqual(event.organizer, self.organizer)
        codes = set(EventPermit.objects.filter(event=event).values_list("permit_type__code", flat=True))
        self.assertEqual(codes, {"ALWAYS_T", "FOOD_T"})

    def test_duplicate_titles_get_unique_slugs(self):
        self.client.force_login(self.organizer)
        self.client.post(reverse("events:create"), self.payload())
        self.client.post(reverse("events:create"), self.payload())
        slugs = sorted(Event.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, ["night-market", "night-market-2"])

    def test_inline_venue_is_created(self):
        self.client.force_login(self.organizer)
        data = self.payload(venue="", new_venue_name="Courtyard", new_venue_address="Mabolo St",
                            new_venue_barangay="Mabolo", new_venue_district=self.district.pk)
        self.client.post(reverse("events:create"), data)
        self.assertTrue(Venue.objects.filter(name="Courtyard").exists())

    def test_end_before_start_is_rejected(self):
        self.client.force_login(self.organizer)
        response = self.client.post(reverse("events:create"),
                                    self.payload(end_at="2030-12-05T08:00"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)

    def test_ticketed_event_needs_fee(self):
        self.client.force_login(self.organizer)
        response = self.client.post(reverse("events:create"), self.payload(is_ticketed="on"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)

    def test_only_owner_can_edit(self):
        event = make_event(self.organizer, self.venue)
        other = User.objects.create_user("org2", password="pw-12345-test", role="ORGANIZER")
        self.client.force_login(other)
        response = self.client.get(reverse("events:edit", args=[event.slug]))
        self.assertEqual(response.status_code, 404)
