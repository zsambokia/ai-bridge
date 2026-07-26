import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("projects", "0009_closure_authority_fields")]

    operations = [
        migrations.CreateModel(
            name="ConversationOrchestration",
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
                ("product_owner_identity", models.CharField(max_length=255)),
                ("confirmation_reference", models.CharField(max_length=255)),
                ("proposal_version", models.PositiveIntegerField()),
                ("proposal_hash", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(default="CONFIRMATION_RECEIVED", max_length=64),
                ),
                ("current_step", models.CharField(default="APPROVAL", max_length=64)),
                ("failure_detail", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contract",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conversation_orchestrations",
                        to="projects.executioncontract",
                    ),
                ),
                (
                    "preparation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conversation_orchestrations",
                        to="projects.executionpreparation",
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conversation_orchestrations",
                        to="projects.executionrun",
                    ),
                ),
                (
                    "scope",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orchestrations",
                        to="projects.executablescope",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("scope", "confirmation_reference"),
                        name="unique_conversation_confirmation",
                    )
                ]
            },
        ),
    ]
