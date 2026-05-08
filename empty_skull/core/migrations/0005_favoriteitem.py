from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_set_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("required_quantity", models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("consumable", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.consumable")),
                ("tool", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.tool")),
            ],
            options={"ordering": ("created_at", "id")},
        ),
    ]
