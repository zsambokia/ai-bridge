# Generated manually for Sprint 005 execution-contract persistence.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0002_projectresolutioncontinuation")]

    operations = [
        migrations.CreateModel(
            name="ExecutionContract",
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
                ("handoff_identifier", models.CharField(max_length=255, unique=True)),
                ("approved_sprint_path", models.CharField(max_length=255)),
                (
                    "lifecycle",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("VALIDATED", "Validated"),
                            ("ISSUED", "Issued"),
                            ("CONSUMED", "Consumed"),
                            ("COMPLETED", "Completed"),
                            ("SUPERSEDED", "Superseded"),
                            ("REVOKED", "Revoked"),
                        ],
                        default="DRAFT",
                        max_length=16,
                    ),
                ),
                ("payload", models.JSONField(default=dict)),
                ("contract_hash", models.CharField(max_length=64)),
                ("validation_errors", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("validated_at", models.DateTimeField(blank=True, null=True)),
                ("issued_at", models.DateTimeField(blank=True, null=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="execution_contracts",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        )
    ]
