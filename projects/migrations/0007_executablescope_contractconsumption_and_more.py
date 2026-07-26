# Generated manually for the Sprint 010 canonical scope authority.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0006_executionrun_executionprogressevent")]

    operations = [
        migrations.CreateModel(
            name="ExecutableScope",
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
                ("identifier", models.CharField(max_length=160, unique=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[("SPRINT", "Sprint"), ("WORK_ITEM", "Work Item")],
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("PROPOSED", "Proposed"),
                            ("APPROVED", "Approved"),
                            ("ACTIVE", "Active"),
                            ("COMPLETED", "Completed"),
                            ("CANCELLED", "Cancelled"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        default="PROPOSED",
                        max_length=16,
                    ),
                ),
                ("version", models.PositiveIntegerField(default=1)),
                ("record", models.JSONField(default=dict)),
                ("approval_reference", models.CharField(blank=True, max_length=128)),
                ("published_path", models.CharField(blank=True, max_length=255)),
                ("content_hash", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="scopes",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["identifier", "version"]},
        ),
        migrations.CreateModel(
            name="ContractConsumption",
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
                ("provider_identity", models.CharField(max_length=255)),
                ("expected_contract_hash", models.CharField(max_length=64)),
                ("observed_baseline", models.CharField(max_length=64)),
                ("schema_version", models.CharField(max_length=32)),
                ("consumed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contract",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="consumption",
                        to="projects.executioncontract",
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="executioncontract",
            name="lifecycle",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Draft"),
                    ("VALIDATED", "Validated"),
                    ("ISSUED", "Issued"),
                    ("CONSUMED", "Consumed"),
                    ("COMPLETED", "Completed"),
                    ("SUPERSEDED", "Superseded"),
                    ("REVOKED", "Revoked"),
                    ("RUNNING", "Running"),
                    ("FAILED", "Failed"),
                    ("CANCELLED", "Cancelled"),
                    ("EXPIRED", "Expired"),
                ],
                default="DRAFT",
                max_length=16,
            ),
        ),
    ]
