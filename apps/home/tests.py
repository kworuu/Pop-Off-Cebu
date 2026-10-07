from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from apps.events.constants import EVENT_PENDING
from apps.events.tests import EventTestBase, make_event


class HomeTests(EventTestBase):
    def test_empty_state_when_no_events(self):
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pop-ups are scheduled yet")

    def test_shows_next_up_and_coming_events(self):
        now = timezone.now()
        make_event(self.organizer, self.venue, title="First one", slug="first",
                   start_at=now + timedelta(days=1), end_at=now + timedelta(days=1, hours=3))
        make_event(self.organizer, self.venue, title="Second one", slug="second",
                   start_at=now + timedelta(days=2), end_at=now + timedelta(days=2, hours=3))
        make_event(self.organizer, self.venue, title="Hidden draft", slug="draft",
                   status=EVENT_PENDING)
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.context["next_up"].title, "First one")
        self.assertEqual([e.title for e in response.context["coming"]], ["Second one"])
        self.assertNotContains(response, "Hidden draft")

    def test_anonymous_lanes_point_to_registration(self):
        response = self.client.get(reverse("home:home"))
        urls = {lane["url"] for lane in response.context["lanes"]}
        self.assertEqual(urls, {reverse("register:register")})

    def test_organizer_lane_goes_to_create(self):
        self.client.force_login(self.organizer)
        response = self.client.get(reverse("home:home"))
        organizer_lane = response.context["lanes"][0]
        self.assertEqual(organizer_lane["url"], reverse("events:create"))
