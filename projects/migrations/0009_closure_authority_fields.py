import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0008_executioncontract_completion_data")]
    operations = [
        migrations.AddField(
            model_name="governanceapproval",
            name="scope",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                related_name="approvals",
                to="projects.executablescope",
            ),
        ),
        migrations.AddField(
            model_name="contractconsumption",
            name="receipt",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="contractconsumption",
            name="idempotency_key",
            field=models.CharField(default="legacy", max_length=128),
        ),
        migrations.AddField(
            model_name="executionrun",
            name="completion_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
