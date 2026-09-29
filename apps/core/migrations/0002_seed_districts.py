from django.db import migrations

DISTRICTS = [
    ("cebu_city", "Cebu City"),
    ("mandaue", "Mandaue City"),
    ("lapu_lapu", "Lapu-Lapu City"),
    ("talisay", "Talisay City"),
]


def seed_districts(apps, schema_editor):
    District = apps.get_model("core", "District")
    for slug, name in DISTRICTS:
        District.objects.get_or_create(slug=slug, defaults={"name": name})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_districts, reverse_code=noop),
    ]