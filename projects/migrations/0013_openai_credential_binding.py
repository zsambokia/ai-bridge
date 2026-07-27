from typing import Any

from django.db import migrations


def bind_openai_to_environment_reference(apps: Any, schema_editor: Any) -> None:
    Provider = apps.get_model("projects", "ExecutionProvider")
    Provider.objects.filter(provider_id="openai").update(
        credential_binding="OPENAI_API_KEY"
    )


class Migration(migrations.Migration):
    dependencies = [("projects", "0012_executionprovider_health_status")]

    operations = [
        migrations.RunPython(
            bind_openai_to_environment_reference,
            migrations.RunPython.noop,
        )
    ]
