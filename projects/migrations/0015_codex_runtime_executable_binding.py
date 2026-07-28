from typing import Any

from django.db import migrations


def configure_codex_runtime_reference(apps: Any, schema_editor: Any) -> None:
    Provider = apps.get_model("projects", "ExecutionProvider")
    Provider.objects.filter(provider_id="codex-cli").update(
        configuration={"runtime_executable_environment": "BRIDGE_CODEX_EXECUTABLE"}
    )


class Migration(migrations.Migration):
    dependencies = [("projects", "0014_codex_provider_relationship")]

    operations = [
        migrations.RunPython(
            configure_codex_runtime_reference, migrations.RunPython.noop
        )
    ]
