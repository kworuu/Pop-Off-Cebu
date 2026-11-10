"""
Seed lookup data: districts, categories, permit types.

    python manage.py seed_reference

Safe to re-run (upserts by slug / code).

IMPORTANT: the permit rows below are PLACEHOLDERS drawn from the project
spec. Confirm office names, required documents and processing times with
the actual LGU offices, then maintain them in the Django admin.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import District
from apps.events.models import Category
from apps.permits.models import PermitType

DISTRICTS = ["Cebu City", "Mandaue City", "Lapu-Lapu City", "Talisay City"]

CATEGORIES = [
    "Artisan Crafts",
    "Food & Gastronomy",
    "Music & Live Performance",
    "Thrift & Sustainable Fashion",
]

# (code, name, issuing_office, scope, trigger_rule)
PERMITS = [
    ("BARANGAY_CLEARANCE", "Barangay Clearance / Resolution",
     "Barangay Hall of the venue's barangay", "EVENT", "ALWAYS"),
    # TODO: replace ALWAYS with a has_commercial_activity flag on Event.
    ("MAYOR_SPECIAL_PERMIT", "Mayor's Special Event / Temporary Trade Fair Permit",
     "Office of the City Mayor", "EVENT", "ALWAYS"),
    ("FIRE_SAFETY", "Fire Safety Clearance",
     "Bureau of Fire Protection", "EVENT", "CROWD_100"),
    ("SANITARY_EVENT", "Sanitary Permit (food handling)",
     "City Health Department", "EVENT", "HAS_FOOD"),
    ("TRAFFIC_ROAD_CLOSURE", "Traffic Management / Road Closure Permit",
     "Cebu City Transportation Office (CCTO)", "EVENT", "ROAD_CLOSURE"),
    ("HEALTH_CARD", "Health Card",
     "City Health Department", "VENDOR", "VENDOR_FOOD"),
    ("SANITARY_TRAINING", "Sanitary Training Certificate",
     "City Health Department", "VENDOR", "VENDOR_FOOD"),
]


class Command(BaseCommand):
    help = "Seed districts, event categories and LGU permit types (placeholders)."

    def handle(self, *args, **options):
        for name in DISTRICTS:
            District.objects.update_or_create(slug=slugify(name), defaults={"name": name})
        for name in CATEGORIES:
            Category.objects.update_or_create(slug=slugify(name), defaults={"name": name})
        for code, name, office, scope, rule in PERMITS:
            PermitType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "issuing_office": office,
                    "scope": scope,
                    "trigger_rule": rule,
                    "description": "Placeholder entry. Verify requirements with the issuing office.",
                },
            )
        self.stdout.write(self.style.SUCCESS("Reference data seeded."))
