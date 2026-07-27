from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0011_executionprovider_providerauditevent")]

    operations = [
        migrations.AddField(
            model_name="executionprovider",
            name="health_status",
            field=models.CharField(
                choices=[
                    ("UNKNOWN", "Unknown"),
                    ("HEALTHY", "Healthy"),
                    ("DEGRADED", "Degraded"),
                    ("UNAVAILABLE", "Unavailable"),
                    ("MISCONFIGURED", "Misconfigured"),
                ],
                default="UNKNOWN",
                max_length=32,
            ),
        )
    ]
