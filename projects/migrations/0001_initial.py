# Generated manually for the Sprint 003 canonical Project domain.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
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
                ("project_id", models.CharField(max_length=128, unique=True)),
                ("display_name", models.CharField(max_length=255)),
                ("repository_full_name", models.CharField(max_length=255, unique=True)),
                ("definition_path", models.CharField(max_length=255)),
                (
                    "lifecycle",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                (
                    "onboarding_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("READY", "Ready"),
                            ("INVALID", "Invalid"),
                        ],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("onboarding_reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["project_id"]},
        ),
        migrations.CreateModel(
            name="ProjectContext",
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
                ("repository_full_name", models.CharField(max_length=255)),
                ("constitution_path", models.CharField(max_length=255)),
                ("roadmap_path", models.CharField(max_length=255)),
                ("sprint_path", models.CharField(max_length=255)),
                ("current_state_path", models.CharField(max_length=255)),
                ("release_gate_configuration", models.JSONField(default=list)),
                (
                    "validation_status",
                    models.CharField(
                        choices=[
                            ("VALID", "Valid"),
                            ("INVALID", "Invalid"),
                            ("STALE", "Stale"),
                        ],
                        max_length=16,
                    ),
                ),
                ("validation_reason", models.TextField(blank=True)),
                ("source_commit_sha", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contexts",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
