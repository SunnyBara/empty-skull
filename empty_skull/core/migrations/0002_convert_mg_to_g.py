from django.db import migrations


def convert_mg_to_g(apps, schema_editor):
    Consumable = apps.get_model("core", "Consumable")
    Consumable.objects.filter(dimension="mg").update(dimension="g")


def revert_g_to_mg(apps, schema_editor):
    Consumable = apps.get_model("core", "Consumable")
    Consumable.objects.filter(dimension="g").update(dimension="mg")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(convert_mg_to_g, revert_g_to_mg),
    ]
