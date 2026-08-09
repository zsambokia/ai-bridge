"""The only Runtime 2.0 provider invocation boundary for operational work."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from time import perf_counter
from typing import Any

from .providers import (
    CodexCliAdapter,
    ProviderStart,
    adapter_for,
    check_health,
    credential_value,
    mark_runtime_unavailable,
    model_adapter_for,
    model_identifier,
    model_text_response,
    select_model_provider,
    select_provider,
)

__all__ = [
    "CodexCliAdapter",
    "ModelProviderAuthenticationUnavailable",
    "ModelProviderSelectionUnavailable",
    "ProviderGatewayError",
    "ProviderStart",
    "adapter_for",
    "check_health",
    "invoke_factory_chat_model",
    "mark_runtime_unavailable",
    "select_factory_chat_model",
    "select_provider",
]


class ProviderGatewayError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ModelProviderSelectionUnavailable(ValueError):
    """No eligible model provider was selected by the Gateway registry query."""


class ModelProviderAuthenticationUnavailable(ValueError):
    """The Gateway cannot use the selected provider credential binding."""


def select_factory_chat_model() -> tuple[Any, str]:
    """Resolve the Factory Chat model without exposing provider selection upstream."""
    identity = os.environ.get("AI_BRIDGE_FACTORY_ORKI_PROVIDER", "openai")
    try:
        entry = select_model_provider(identity)
    except ValueError as exc:
        raise ModelProviderSelectionUnavailable(str(exc)) from exc
    try:
        # Validate the non-secret binding only.  The resolved credential is never
        # returned, persisted, or exposed to conversation or engine code.
        credential_value(entry)
    except ValueError as exc:
        raise ModelProviderAuthenticationUnavailable(str(exc)) from exc
    return entry, model_identifier(entry)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def invoke_factory_chat_model(
    *,
    session: object,
    owner_body: str,
    context_builder: Callable[[Any], dict[str, object]],
    prompt_builder: Callable[[dict[str, object], str], str],
    response_decoder: Callable[
        [str], tuple[str, dict[str, object] | None, dict[str, object]]
    ],
    model_adapter_resolver: Callable[..., Any] = model_adapter_for,
    model_text_decoder: Callable[..., str] = model_text_response,
) -> dict[str, Any]:
    """Select, invoke and normalize a model response without domain mutation.

    The caller supplies Mission Resolution's context, prompt and response
    semantics.  The Gateway remains a provider boundary and must not import a
    Conversation or Mission module to obtain them.
    """

    try:
        entry, model = select_factory_chat_model()
    except ModelProviderSelectionUnavailable as error:
        raise ProviderGatewayError("MODEL_PROVIDER_UNAVAILABLE", str(error)) from error
    except ModelProviderAuthenticationUnavailable as error:
        raise ProviderGatewayError(
            "PROVIDER_CREDENTIAL_UNAVAILABLE", str(error)
        ) from error
    context_package = context_builder(session)
    prompt = prompt_builder(context_package, owner_body)
    started = perf_counter()
    try:
        adapter = model_adapter_resolver(entry)
        raw: dict[str, object] | None = None
        attempts = 0
        for attempts in range(1, 3):
            try:
                raw = adapter.invoke_model(entry, prompt)
                break
            except (OSError, TimeoutError):
                if attempts == 2:
                    raise
        if raw is None:
            raise OSError("ORKI_MODEL_REQUEST_FAILED")
        response_text = model_text_decoder(entry, raw)
        response, provider_plan, understanding = response_decoder(response_text)
    except (ValueError, OSError, TimeoutError) as error:
        raise ProviderGatewayError(type(error).__name__.upper(), str(error)) from error
    return {
        "response": response,
        "provider_plan": provider_plan,
        "understanding": understanding,
        "raw": raw,
        "provider_id": entry.provider_id,
        "model": model,
        "prompt_hash": _hash(prompt),
        "response_hash": _hash(response_text),
        "context_package_hash": _hash(json.dumps(context_package, sort_keys=True)),
        "latency_ms": round((perf_counter() - started) * 1000),
        "attempts": attempts,
        "evidence_references": [
            {"provider_id": entry.provider_id, "model": model, "attempts": attempts}
        ],
    }
