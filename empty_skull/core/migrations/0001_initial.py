from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Consumable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=10)),
                ("dimension", models.CharField(choices=[("ml", "ml"), ("g", "g"), ("piece", "piece")], max_length=10)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Set",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Tool",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("usage_count", models.PositiveIntegerField(verbose_name="utilisations")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="SetItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("required_quantity", models.DecimalField(decimal_places=2, max_digits=10)),
                ("consumable", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.consumable")),
                ("set", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="core.set")),
                ("tool", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.tool")),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("current_quantity", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=10)),
                ("consumable", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.consumable")),
                ("tool", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.tool")),
            ],
            options={"ordering": ("tool__name", "consumable__name")},
        ),
    ]
