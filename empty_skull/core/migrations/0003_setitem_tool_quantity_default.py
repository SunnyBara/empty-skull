from decimal import Decimal

from django.db import migrations, models


def normalize_tool_quantities(apps, schema_editor):
    SetItem = apps.get_model("core", "SetItem")
    SetItem.objects.exclude(tool=None).update(required_quantity=Decimal("1.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_convert_mg_to_g"),
    ]

    operations = [
        migrations.AlterField(
            model_name="setitem",
            name="required_quantity",
            field=models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=10),
        ),
        migrations.RunPython(normalize_tool_quantities, migrations.RunPython.noop),
    ]
