# ruff: noqa: E501
# Generated manually for sprint 11489ce0-85b6-4bad-897e-d16d76b2f71c.

import uuid
from typing import Any

import django.db.models.deletion
from django.db import migrations, models


def migrate_factory_conversations(apps: Any, schema_editor: Any) -> None:
    FactoryChatSession = apps.get_model("projects", "FactoryChatSession")
    FactoryChatMessage = apps.get_model("projects", "FactoryChatMessage")
    Conversation = apps.get_model("projects", "Conversation")
    ConversationState = apps.get_model("projects", "ConversationState")
    ConversationMessage = apps.get_model("projects", "ConversationMessage")

    for session in FactoryChatSession.objects.exclude(project__isnull=True).iterator():
        conversation = Conversation.objects.create(
            token=uuid.uuid4(),
            project_id=session.project_id,
            actor_identity=session.actor_identity,
        )
        ConversationState.objects.create(conversation_id=conversation.pk)
        session.conversation_id = conversation.pk
        session.save(update_fields=["conversation"])
        for message in FactoryChatMessage.objects.filter(
            session_id=session.pk
        ).iterator():
            ConversationMessage.objects.create(
                conversation_id=conversation.pk,
                role="OWNER" if message.role == "OWNER" else "ASSISTANT",
                body=message.body,
                correlation_id=message.correlation_id,
                provenance={"migrated_from_factory_chat_message": message.pk},
            )


class Migration(migrations.Migration):
    dependencies = [("projects", "0067_factory_development_execution_profile")]

    operations = [
        migrations.CreateModel(
            name="ContextProfile",
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
                ("profile_hash", models.CharField(max_length=64, unique=True)),
                ("persona_or_role", models.CharField(blank=True, max_length=128)),
                ("purpose_or_capability", models.CharField(max_length=128)),
                ("scope", models.JSONField(default=dict)),
                ("policy", models.JSONField(default=dict)),
                ("inputs", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="context_profiles",
                        to="projects.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Conversation",
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
                ("actor_identity", models.CharField(max_length=255)),
                ("persona_reference", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conversations",
                        to="projects.project",
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="ConversationDecision",
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
                ("statement", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PROPOSED", "Proposed"),
                            ("ACCEPTED", "Accepted"),
                            ("CHALLENGED", "Challenged"),
                            ("SUPERSEDED", "Superseded"),
                        ],
                        max_length=16,
                    ),
                ),
                ("evidence", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="decisions",
                        to="projects.conversation",
                    ),
                ),
                (
                    "supersedes",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="replacements",
                        to="projects.conversationdecision",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ConversationMessage",
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
                    "role",
                    models.CharField(
                        choices=[
                            ("OWNER", "Product Owner"),
                            ("ASSISTANT", "Assistant"),
                            ("SYSTEM", "System"),
                        ],
                        max_length=16,
                    ),
                ),
                ("body", models.TextField()),
                ("correlation_id", models.CharField(blank=True, max_length=128)),
                ("provenance", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="projects.conversation",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "pk"]},
        ),
        migrations.CreateModel(
            name="ConversationState",
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
                    "semantic_state",
                    models.CharField(
                        choices=[
                            ("EXPLORING", "Exploring"),
                            ("DESIGNING", "Designing"),
                            ("PROPOSAL_READY", "Proposal ready"),
                            ("DECISION_PENDING", "Decision pending"),
                            ("DECIDED", "Decided"),
                        ],
                        default="EXPLORING",
                        max_length=32,
                    ),
                ),
                (
                    "lifecycle_status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("DEFERRED", "Deferred"),
                            ("CLOSED", "Closed"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                ("readiness_conditions", models.JSONField(default=dict)),
                ("version", models.PositiveIntegerField(default=1)),
                ("transition_evidence", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "conversation",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="state",
                        to="projects.conversation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MissionResolution",
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
                            ("NEW_MISSION", "New Mission"),
                            ("UPDATE_MISSION", "Update Mission"),
                            ("CLOSE_MISSION", "Close Mission"),
                            ("NO_RUNTIME_ACTION", "No runtime action"),
                        ],
                        max_length=32,
                    ),
                ),
                ("rationale", models.TextField()),
                ("evidence", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "conversation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="mission_resolutions",
                        to="projects.conversation",
                    ),
                ),
            ],
        ),
        migrations.RenameModel(
            old_name="KnowledgeContextPackage", new_name="ContextPackage"
        ),
        migrations.AddField(
            model_name="contextpackage",
            name="context_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="packages",
                to="projects.contextprofile",
            ),
        ),
        migrations.AddField(
            model_name="factorychatsession",
            name="conversation",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="factory_chat_session",
                to="projects.conversation",
            ),
        ),
        migrations.RunPython(migrate_factory_conversations, migrations.RunPython.noop),
    ]
