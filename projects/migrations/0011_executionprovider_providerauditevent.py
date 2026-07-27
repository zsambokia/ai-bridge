from typing import Any

from django.db import migrations, models


def seed_providers(apps: Any, schema_editor: Any) -> None:
    Provider = apps.get_model("projects", "ExecutionProvider")
    providers = (
        {
            "provider_id": "codex-cli",
            "name": "Codex CLI",
            "kind": "CODEX",
            "role": "EXECUTION_AGENT",
            "status": "ACTIVE",
            "adapter_key": "codex-cli",
            "enabled": True,
            "priority": 1,
            "capabilities": [
                "CODE_EXECUTION",
                "CANCELLATION",
                "STATUS_POLLING",
                "HEALTH_CHECK",
            ],
        },
        {
            "provider_id": "openai",
            "name": "OpenAI API",
            "kind": "OPENAI",
            "role": "MODEL_API",
            "status": "DRAFT",
            "adapter_key": "openai",
            "capabilities": ["MODEL_INFERENCE", "USAGE_REPORTING", "HEALTH_CHECK"],
        },
        {
            "provider_id": "claude",
            "name": "Claude API",
            "kind": "CLAUDE",
            "role": "MODEL_API",
            "status": "DRAFT",
            "adapter_key": "claude",
            "capabilities": ["MODEL_INFERENCE", "USAGE_REPORTING", "HEALTH_CHECK"],
        },
        {
            "provider_id": "github",
            "name": "GitHub API",
            "kind": "GITHUB",
            "role": "REPOSITORY_SERVICE",
            "status": "DRAFT",
            "adapter_key": "github",
            "capabilities": [
                "REPOSITORY_READ",
                "REPOSITORY_WRITE",
                "BRANCH_MANAGEMENT",
                "PULL_REQUEST_MANAGEMENT",
                "HEALTH_CHECK",
            ],
        },
        {
            "provider_id": "bigquery",
            "name": "BigQuery API",
            "kind": "BIGQUERY",
            "role": "DATA_SERVICE",
            "status": "DRAFT",
            "adapter_key": "bigquery",
            "capabilities": ["DATA_QUERY_READ", "DATA_QUERY_WRITE", "HEALTH_CHECK"],
        },
    )
    for provider in providers:
        provider_id = provider["provider_id"]
        Provider.objects.get_or_create(provider_id=provider_id, defaults=provider)


class Migration(migrations.Migration):
    dependencies = [("projects", "0010_conversationorchestration")]
    operations = [
        migrations.CreateModel(
            name="ExecutionProvider",
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
                ("provider_id", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=128)),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("CODEX", "Codex CLI"),
                            ("OPENAI", "OpenAI"),
                            ("CLAUDE", "Claude"),
                            ("GITHUB", "GitHub"),
                            ("BIGQUERY", "BigQuery"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("EXECUTION_AGENT", "Execution agent"),
                            ("MODEL_API", "Model API"),
                            ("REPOSITORY_SERVICE", "Repository service"),
                            ("DATA_SERVICE", "Data service"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("ACTIVE", "Active"),
                            ("DISABLED", "Disabled"),
                            ("UNAVAILABLE", "Unavailable"),
                            ("MISCONFIGURED", "Misconfigured"),
                            ("DEPRECATED", "Deprecated"),
                        ],
                        default="DRAFT",
                        max_length=32,
                    ),
                ),
                ("adapter_key", models.CharField(max_length=64, unique=True)),
                ("enabled", models.BooleanField(default=False)),
                ("priority", models.PositiveIntegerField(default=100)),
                ("configuration", models.JSONField(blank=True, default=dict)),
                ("credential_binding", models.CharField(blank=True, max_length=128)),
                ("capabilities", models.JSONField(blank=True, default=list)),
                ("health", models.JSONField(blank=True, default=dict)),
                ("last_health_at", models.DateTimeField(blank=True, null=True)),
                ("last_test_result", models.JSONField(blank=True, default=dict)),
                ("first_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["priority", "provider_id"]},
        ),
        migrations.CreateModel(
            name="ProviderAuditEvent",
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
                ("action", models.CharField(max_length=64)),
                ("details", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="audit_events",
                        to="projects.executionprovider",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.RunPython(seed_providers, migrations.RunPython.noop),
    ]
