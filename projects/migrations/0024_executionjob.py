import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0023_engineeringentity_engineeringentityrevision_and_more")
    ]

    operations = [
        migrations.CreateModel(
            name="ExecutionJob",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("QUEUED", "Queued"),
                            ("LEASED", "Leased"),
                            ("STARTED", "Started"),
                            ("FAILED", "Failed"),
                        ],
                        default="QUEUED",
                        max_length=16,
                    ),
                ),
                ("lease_owner", models.CharField(blank=True, max_length=128)),
                ("lease_expires_at", models.DateTimeField(blank=True, null=True)),
                ("last_heartbeat_at", models.DateTimeField(blank=True, null=True)),
                (
                    "provider_attempt_metadata",
                    models.JSONField(blank=True, default=dict),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "run",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="queue_job",
                        to="projects.executionrun",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
