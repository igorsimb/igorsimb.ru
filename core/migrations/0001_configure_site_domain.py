from django.db import migrations


def configure_site_domain(apps, schema_editor):
    site_model = apps.get_model("sites", "Site")
    site_model.objects.update_or_create(
        pk=1,
        defaults={"domain": "igorsimb.ru", "name": "igorsimb.ru"},
    )


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(configure_site_domain, migrations.RunPython.noop),
    ]
