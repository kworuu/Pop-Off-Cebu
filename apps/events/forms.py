from django import forms

from apps.core.models import District

from .constants import RSVP_CHOICES
from .models import Announcement, Category, Event, Venue

DT_FORMAT = "%Y-%m-%dT%H:%M"


class EventForm(forms.ModelForm):
    """
    Organizer create/edit form.

    Venue is either picked from existing venues or created inline from the
    new_venue_* fields. The view calls resolve_venue() inside its transaction,
    so a failed event save never leaves an orphan venue behind.
    """

    venue = forms.ModelChoiceField(
        queryset=Venue.objects.select_related("district").order_by("name"),
        required=False,
        empty_label="New venue (fill in the fields below)",
    )
    new_venue_name = forms.CharField(max_length=150, required=False, label="Venue name")
    new_venue_address = forms.CharField(max_length=255, required=False, label="Street address")
    new_venue_barangay = forms.CharField(max_length=100, required=False, label="Barangay")
    new_venue_district = forms.ModelChoiceField(
        queryset=District.objects.order_by("name"), required=False, label="City / district"
    )

    field_order = [
        "title", "description", "categories",
        "venue", "new_venue_name", "new_venue_address",
        "new_venue_barangay", "new_venue_district",
        "start_at", "end_at", "expected_attendance",
        "has_food_stalls", "involves_road_closure",
        "is_ticketed", "admission_fee",
    ]

    class Meta:
        model = Event
        fields = (
            "title", "description", "start_at", "end_at", "expected_attendance",
            "is_ticketed", "admission_fee", "has_food_stalls",
            "involves_road_closure", "categories",
        )
        labels = {
            "start_at": "Starts",
            "end_at": "Ends",
            "expected_attendance": "Expected attendance",
            "is_ticketed": "Ticketed event",
            "admission_fee": "Admission fee (PHP)",
            "has_food_stalls": "Food or drink will be sold or served",
            "involves_road_closure": "Needs a road closure or rerouting",
            "categories": "Categories",
        }
        help_texts = {
            "expected_attendance": "Your best estimate. It decides which clearances apply.",
            "categories": "Pick at least one so attendees can find you.",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
            "categories": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("start_at", "end_at"):
            self.fields[name].input_formats = [DT_FORMAT, "%Y-%m-%dT%H:%M:%S"]
        self.fields["categories"].queryset = Category.objects.order_by("name")
        self.fields["categories"].required = True
        self.fields["expected_attendance"].min_value = 1
        if self.instance.pk:
            self.fields["venue"].initial = self.instance.venue_id

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_at"), cleaned.get("end_at")
        if start and end and end <= start:
            self.add_error("end_at", "End time must be after the start time.")

        if cleaned.get("is_ticketed"):
            fee = cleaned.get("admission_fee")
            if fee is None or fee < 0:
                self.add_error("admission_fee", "Enter the admission fee for a ticketed event.")
        else:
            cleaned["admission_fee"] = None

        if not cleaned.get("venue"):
            required = {
                "new_venue_name": "Enter the venue name.",
                "new_venue_address": "Enter the street address.",
                "new_venue_barangay": "Enter the barangay.",
                "new_venue_district": "Choose the city or district.",
            }
            for name, message in required.items():
                if not cleaned.get(name):
                    self.add_error(name, message)
        return cleaned

    def resolve_venue(self):
        """Return the chosen venue, creating one from the inline fields if needed."""
        venue = self.cleaned_data.get("venue")
        if venue:
            return venue
        data = self.cleaned_data
        return Venue.objects.create(
            name=data["new_venue_name"],
            address=data["new_venue_address"],
            barangay=data["new_venue_barangay"],
            district=data["new_venue_district"],
        )


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("subject", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}


class RSVPForm(forms.Form):
    status = forms.ChoiceField(choices=RSVP_CHOICES)
    party_size = forms.IntegerField(min_value=1, max_value=20, initial=1)


class EventFilterForm(forms.Form):
    WHEN_CHOICES = [
        ("upcoming", "All upcoming"),
        ("today", "Today"),
        ("weekend", "This weekend"),
    ]

    q = forms.CharField(required=False, label="Search")
    district = forms.ModelChoiceField(
        queryset=District.objects.order_by("name"),
        to_field_name="slug", required=False, empty_label="All districts",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by("name"),
        to_field_name="slug", required=False, empty_label="All categories",
    )
    when = forms.ChoiceField(choices=WHEN_CHOICES, required=False, label="When")
    date = forms.DateField(
        required=False, label="On a specific date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
