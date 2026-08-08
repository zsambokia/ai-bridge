"""Explicit, pure contracts for candidates emitted by the canonical Runtime."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

RUNTIME_CANDIDATE_SCHEMA_VERSION = "RuntimeCandidate.v1"

FORBIDDEN_RUNTIME_CANDIDATE_FIELDS = frozenset(
    {
        "embedding",
        "embedding_vector",
        "vector",
        "vector_id",
        "vector_row",
        "vector_store",
        "knowledge_entry",
        "knowledge_entry_id",
        "activation",
        "activation_status",
        "activated",
        "index",
        "index_id",
        "lifecycle",
        "akb",
        "akb_id",
        "knowledge_document",
    }
)


class RuntimeCandidateValidationError(ValueError):
    """Raised when a Runtime candidate violates its pure contract."""


class RuntimeCandidateImmutableError(ValueError):
    """Raised when a persisted Runtime candidate is changed."""


def assert_no_forbidden_fields(value: object) -> None:
    """Reject knowledge-pipeline ownership fields at every nesting depth."""
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if (
                isinstance(key, str)
                and key.strip().lower() in FORBIDDEN_RUNTIME_CANDIDATE_FIELDS
            ):
                raise RuntimeCandidateValidationError(
                    f"RUNTIME_CANDIDATE_FORBIDDEN_FIELD:{key.strip().lower()}"
                )
            assert_no_forbidden_fields(nested_value)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            assert_no_forbidden_fields(item)


def _validate_fields(
    value: Mapping[str, Any], *, required: frozenset[str], allowed: frozenset[str]
) -> None:
    assert_no_forbidden_fields(value)
    unknown = set(value).difference(allowed)
    if unknown:
        raise RuntimeCandidateValidationError(
            f"RUNTIME_CANDIDATE_UNKNOWN_FIELDS:{','.join(sorted(unknown))}"
        )
    missing = required.difference(value)
    if missing:
        raise RuntimeCandidateValidationError(
            f"RUNTIME_CANDIDATE_REQUIRED_FIELDS:{','.join(sorted(missing))}"
        )


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeCandidateValidationError(f"RUNTIME_CANDIDATE_INVALID_TEXT:{field}")
    return value.strip()


def _confidence(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeCandidateValidationError("RUNTIME_CANDIDATE_INVALID_CONFIDENCE")
    normalized = float(value)
    if not 0.0 <= normalized <= 1.0:
        raise RuntimeCandidateValidationError("RUNTIME_CANDIDATE_INVALID_CONFIDENCE")
    return normalized


class RuntimeReflectionCandidateValidator:
    """Validator for reflection candidates owned only by the Runtime."""

    REQUIRED_FIELDS = frozenset({"summary", "reflection_text", "confidence"})
    ALLOWED_FIELDS = REQUIRED_FIELDS

    @classmethod
    def validate_input(cls, value: Mapping[str, Any]) -> dict[str, object]:
        _validate_fields(
            value, required=cls.REQUIRED_FIELDS, allowed=cls.ALLOWED_FIELDS
        )
        return {
            "summary": _required_text(value["summary"], "summary"),
            "reflection_text": _required_text(
                value["reflection_text"], "reflection_text"
            ),
            "confidence": _confidence(value["confidence"]),
        }

    @classmethod
    def validate_record(cls, value: Mapping[str, Any]) -> None:
        _validate_fields(
            value,
            required=frozenset(
                {
                    "schema_version",
                    "goal_id",
                    "summary",
                    "reflection_text",
                    "verification_result",
                    "confidence",
                    "evidence_references",
                }
            ),
            allowed=frozenset(
                {
                    "schema_version",
                    "goal_id",
                    "summary",
                    "reflection_text",
                    "verification_result",
                    "confidence",
                    "evidence_references",
                }
            ),
        )
        if value["schema_version"] != RUNTIME_CANDIDATE_SCHEMA_VERSION:
            raise RuntimeCandidateValidationError("RUNTIME_CANDIDATE_SCHEMA_VERSION")
        _required_text(value["summary"], "summary")
        _required_text(value["reflection_text"], "reflection_text")
        _confidence(value["confidence"])
        if not isinstance(value["verification_result"], Mapping):
            raise RuntimeCandidateValidationError(
                "RUNTIME_CANDIDATE_INVALID_VERIFICATION_RESULT"
            )


class RuntimeKnowledgeCandidateValidator:
    """Validator for knowledge candidates awaiting the future Knowledge Pipeline."""

    REQUIRED_FIELDS = frozenset(
        {"title", "summary", "body", "reason", "confidence", "tags"}
    )
    ALLOWED_FIELDS = REQUIRED_FIELDS

    @classmethod
    def validate_input(cls, value: Mapping[str, Any]) -> dict[str, object]:
        _validate_fields(
            value, required=cls.REQUIRED_FIELDS, allowed=cls.ALLOWED_FIELDS
        )
        tags = value["tags"]
        if (
            not isinstance(tags, Sequence)
            or isinstance(tags, (str, bytes))
            or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
        ):
            raise RuntimeCandidateValidationError("RUNTIME_CANDIDATE_INVALID_TAGS")
        return {
            "title": _required_text(value["title"], "title"),
            "summary": _required_text(value["summary"], "summary"),
            "body": _required_text(value["body"], "body"),
            "reason": _required_text(value["reason"], "reason"),
            "confidence": _confidence(value["confidence"]),
            "tags": [tag.strip() for tag in tags],
        }

    @classmethod
    def validate_record(cls, value: Mapping[str, Any]) -> None:
        _validate_fields(
            value,
            required=frozenset(
                {
                    "schema_version",
                    "title",
                    "summary",
                    "body",
                    "reason",
                    "confidence",
                    "tags",
                    "evidence_references",
                }
            ),
            allowed=frozenset(
                {
                    "schema_version",
                    "title",
                    "summary",
                    "body",
                    "reason",
                    "confidence",
                    "tags",
                    "evidence_references",
                }
            ),
        )
        if value["schema_version"] != RUNTIME_CANDIDATE_SCHEMA_VERSION:
            raise RuntimeCandidateValidationError("RUNTIME_CANDIDATE_SCHEMA_VERSION")
        cls.validate_input({key: value[key] for key in cls.REQUIRED_FIELDS})
