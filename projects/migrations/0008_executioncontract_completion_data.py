# Generated manually for Sprint 010 completion evidence binding.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0007_executablescope_contractconsumption_and_more")]

    operations = [
        migrations.AddField(
            model_name="executioncontract",
            name="completion_data",
            field=models.JSONField(blank=True, default=dict),
        )
    ]
