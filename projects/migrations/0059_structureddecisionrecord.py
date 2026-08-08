# Generated manually for the Sprint 04 Structured Decision audit contract.
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0058_semantic_embedding")]

    operations = [
        migrations.CreateModel(
            name="StructuredDecisionRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("contract_version", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
