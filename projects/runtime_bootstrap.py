"""Project-specific, validated runtime bootstrap profile resolution."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ExecutionRun, RuntimeBootstrapProfile


class BootstrapProfileError(ValueError):
    """A profile is not safe to use for an execution runtime."""


@dataclass(frozen=True)
class BootstrapProfile:
    database: dict[str, object]
    seed_command: list[str]
    services: list[dict[str, object]]
    environment: dict[str, str]


def resolve_profile(run: ExecutionRun) -> BootstrapProfile:
    """Resolve the optional per-project profile; defaults are deterministic."""
    entry = RuntimeBootstrapProfile.objects.filter(project=run.contract.project).first()
    database: object = entry.database if entry else {"mode": "sqlite"}
    seed_command: object = entry.seed_command if entry else []
    services: object = entry.services if entry else []
    environment: object = entry.environment if entry else {}
    if (
        not isinstance(database, dict)
        or database.get("mode", "sqlite") != "sqlite"
        or not isinstance(seed_command, list)
        or not all(isinstance(item, str) and item for item in seed_command)
        or not isinstance(services, list)
        or not all(isinstance(item, dict) for item in services)
        or not isinstance(environment, dict)
        or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in environment.items()
        )
    ):
        raise BootstrapProfileError("RUNTIME_BOOTSTRAP_PROFILE_INVALID")
    for service in services:
        command = service.get("command")
        if not isinstance(service.get("name"), str) or not isinstance(command, list):
            raise BootstrapProfileError("RUNTIME_BOOTSTRAP_SERVICE_INVALID")
        if not all(isinstance(item, str) and item for item in command):
            raise BootstrapProfileError("RUNTIME_BOOTSTRAP_SERVICE_INVALID")
        shutdown = service.get("shutdown_command", [])
        if not isinstance(shutdown, list) or not all(
            isinstance(item, str) and item for item in shutdown
        ):
            raise BootstrapProfileError("RUNTIME_BOOTSTRAP_SERVICE_INVALID")
    return BootstrapProfile(
        database={str(key): value for key, value in database.items()},
        seed_command=seed_command,
        services=services,
        environment={str(key): value for key, value in environment.items()},
    )
