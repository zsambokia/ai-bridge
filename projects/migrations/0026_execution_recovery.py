# Generated manually for the Sprint B durable recovery data model.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0025_external_execution_reconciliation")]

    operations = [
        migrations.AddField(
            model_name="executionjob",
            name="checkpoint",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="executionjob",
            name="next_recovery_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="executionjob",
            name="reconciliation_evidence",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="executionjob",
            name="recovery_attempts",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="executionjob",
            name="status",
            field=models.CharField(
                choices=[
                    ("QUEUED", "Queued"),
                    ("LEASED", "Leased"),
                    ("STARTED", "Started"),
                    ("RECOVERING", "Recovering"),
                    ("RECOVERY_REVIEW_REQUIRED", "Recovery review required"),
                    ("FAILED", "Failed"),
                ],
                default="QUEUED",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="ExecutionRecoveryAttempt",
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
                    "outcome",
                    models.CharField(
                        choices=[
                            ("REATTACH", "Reattach worker"),
                            ("RECOVERING", "Recovering from checkpoint"),
                            ("RECOVERY_REVIEW_REQUIRED", "Recovery review required"),
                            ("NO_ACTION", "No action"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reason", models.CharField(max_length=255)),
                ("evidence", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recovery_history",
                        to="projects.executionjob",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
