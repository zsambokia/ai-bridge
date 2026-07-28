"""Provider integrations and composition for the provider-neutral domain."""

from __future__ import annotations

import json
import os
from typing import Any

from .models import ExecutionProvider
from .orchestrator import OrchestratorProvider, OrchestratorProviderRegistry
from .providers import (
    ModelAdapter,
    model_adapter_for,
    select_model_provider,
    structured_model_response,
)


class RegisteredModelOrchestratorProvider:
    """Bridge the governed model-provider platform into the neutral protocol."""

    def __init__(self, entry: ExecutionProvider, adapter: ModelAdapter) -> None:
        self.entry = entry
        self.adapter = adapter
        self.provider_id = entry.provider_id

    def assess(self, context: dict[str, Any], correlation_id: str) -> dict[str, Any]:
        try:
            prompt = json.dumps(
                {
                    "instruction": (
                        "Return only one JSON object matching orchestration "
                        "schema 1.0. "
                        "Recommendations have no execution authority."
                    ),
                    "correlation_id": correlation_id,
                    "context": context,
                },
                separators=(",", ":"),
            )
            response = self.adapter.invoke_model(self.entry, prompt)
            return structured_model_response(self.entry, response)
        except ValueError as exc:
            raise RuntimeError("ORCHESTRATOR_PROVIDER_RESPONSE_INVALID") from exc


def configured_provider() -> OrchestratorProvider:
    """Resolve the configured provider through the canonical provider registry."""
    identity = os.environ.get("AI_BRIDGE_ORCHESTRATOR_PROVIDER", "openai")
    entry = select_model_provider(identity)
    registry = OrchestratorProviderRegistry()
    registry.register(
        RegisteredModelOrchestratorProvider(entry, model_adapter_for(entry))
    )
    return registry.get(entry.provider_id)
