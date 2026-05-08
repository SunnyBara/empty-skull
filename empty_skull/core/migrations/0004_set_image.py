from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_setitem_tool_quantity_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="set",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="sets/"),
        ),
    ]
