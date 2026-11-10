import django.db.models.deletion
from django.db import migrations, models


def migrate_district_text_to_fk(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    District = apps.get_model("core", "District")
    default_district, _ = District.objects.get_or_create(
        slug="cebu_city", defaults={"name": "Cebu City"}
    )
    for profile in Profile.objects.all():
        district = District.objects.filter(slug=profile.district_old_text).first() or default_district
        profile.district_id_new = district.id
        profile.save(update_fields=["district_id_new"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_districts'),
        ('profiles', '0002_profile_business_or_stage_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'},
        ),
        migrations.AddField(
            model_name='profile',
            name='portfolio_url',
            field=models.URLField(blank=True, default='', help_text='Default link reused on booth and gig applications.'),
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='district',
            new_name='district_old_text',
        ),
        migrations.AddField(
            model_name='profile',
            name='district_id_new',
            field=models.BigIntegerField(null=True),
        ),
        migrations.RunPython(migrate_district_text_to_fk, reverse_code=noop),
        migrations.RemoveField(
            model_name='profile',
            name='district_old_text',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='district_id_new',
            new_name='district',
        ),
        migrations.AlterField(
            model_name='profile',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='core.district'),
        ),
    ]