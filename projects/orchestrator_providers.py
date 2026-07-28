"""Provider integrations and composition for the provider-neutral domain."""

from __future__ import annotations

import json
import os
from typing import Any

from .orchestrator import OrchestratorProvider, OrchestratorProviderRegistry


class OpenAIOrchestratorProvider:
    """OpenAI implementation of the neutral orchestration assessment protocol."""

    provider_id = "openai-orchestrator"

    def __init__(self) -> None:
        self.model = os.environ.get("AI_BRIDGE_ORCHESTRATOR_MODEL", "gpt-5-mini")

    def assess(self, context: dict[str, Any], correlation_id: str) -> dict[str, Any]:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("ORCHESTRATOR_PROVIDER_CREDENTIAL_UNAVAILABLE")
        try:
            from openai import OpenAI

            response = OpenAI().responses.create(
                model=self.model,
                input=[
                    {
                        "role": "developer",
                        "content": (
                            "Return only one JSON object matching orchestration "
                            "schema 1.0. Recommendations have no execution authority."
                        ),
                    },
                    {"role": "user", "content": json.dumps(context)},
                ],
                metadata={"correlation_id": correlation_id},
            )
            return json.loads(response.output_text)
        except (ValueError, TypeError, KeyError) as exc:
            raise RuntimeError("ORCHESTRATOR_PROVIDER_RESPONSE_INVALID") from exc
        except Exception as exc:
            raise RuntimeError("ORCHESTRATOR_PROVIDER_UNAVAILABLE") from exc


def configured_provider() -> OrchestratorProvider:
    """Select a registered adapter at the application boundary, never in domain code."""
    registry = OrchestratorProviderRegistry()
    registry.register(OpenAIOrchestratorProvider())
    return registry.get(
        os.environ.get("AI_BRIDGE_ORCHESTRATOR_PROVIDER", "openai-orchestrator")
    )
