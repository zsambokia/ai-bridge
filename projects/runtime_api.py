"""Read and lifecycle-control API for the provider-independent Orki Runtime."""

from __future__ import annotations

import json
import time

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponseBadRequest,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .models import OrkiExecution
from .orki_runtime import (
    RuntimeTransitionError,
    dispatch_factory_chat_execution,
    execution_projection,
    pause_execution,
    recover_execution,
    resume_execution,
)


def _actor(request: HttpRequest) -> str:
    return request.user.get_username()


def _projection_with_chat_messages(execution: OrkiExecution) -> dict[str, object]:
    """Add the UI transcript only for the Factory Chat Runtime adapter."""
    projection = execution_projection(execution)
    context = execution.provider_context or {}
    if context.get("channel") == "FACTORY_CHAT":
        from .factory_orki import messages_for

        if context.get("correlation_id"):
            projection["messages"] = messages_for(execution.plan.goal.source_session)
    return projection


def _runtime_event_payload(
    projection: dict[str, object], event: dict[str, object] | None = None
) -> dict[str, object]:
    """Emit a self-contained Runtime presentation contract for every SSE event."""
    payload = dict(projection)
    payload["event"] = event
    return payload


@login_required
@require_GET
def runtime_execution_detail(request: HttpRequest, token: str) -> JsonResponse:
    execution = get_object_or_404(OrkiExecution, token=token)
    return JsonResponse(_projection_with_chat_messages(execution))


@login_required
@require_POST
def runtime_execution_dispatch(
    request: HttpRequest, token: str
) -> JsonResponse | HttpResponseBadRequest:
    try:
        execution = dispatch_factory_chat_execution(token, actor=_actor(request))
    except OrkiExecution.DoesNotExist:
        return HttpResponseBadRequest("RUNTIME_EXECUTION_NOT_FOUND")
    except RuntimeTransitionError:
        execution = get_object_or_404(OrkiExecution, token=token)
        projection = _projection_with_chat_messages(execution)
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "RUNTIME_STATE_REQUIRES_ATTENTION",
                    "message": projection["human_message"],
                    "retryable": execution.state.startswith("WAITING_"),
                },
                "execution": projection,
                **projection,
            },
            status=409,
        )
    return JsonResponse(_projection_with_chat_messages(execution))


@login_required
@require_GET
def runtime_execution_event_stream(
    request: HttpRequest, token: str
) -> StreamingHttpResponse:
    """Server-Sent Event projection of the append-only Runtime Event Stream."""
    get_object_or_404(OrkiExecution, token=token)

    def events():
        sequence = 0
        for _ in range(120):  # bounded connection; browser reconnects if needed
            execution = get_object_or_404(OrkiExecution, token=token)
            projection = execution_projection(execution)
            for event in projection["events"]:
                if event["sequence"] > sequence:
                    sequence = event["sequence"]
                    payload = _runtime_event_payload(projection, event)
                    yield f"event: runtime\ndata: {json.dumps(payload)}\n\n"
            snapshot = json.dumps(_runtime_event_payload(projection))
            yield f"event: snapshot\ndata: {snapshot}\n\n"
            if projection["state"] in {
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                "WAITING_EXTERNAL",
            }:
                yield (
                    "event: terminal\ndata: "
                    f"{json.dumps(_runtime_event_payload(projection))}\n\n"
                )
                return
            time.sleep(0.25)

    response = StreamingHttpResponse(events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def _control(
    request: HttpRequest, token: str, action: str
) -> JsonResponse | HttpResponseBadRequest:
    try:
        if action == "pause":
            execution = pause_execution(
                token, actor=_actor(request), reason=request.POST.get("reason", "")
            )
        elif action == "resume":
            execution = resume_execution(token, actor=_actor(request))
        else:
            execution = recover_execution(token, actor=_actor(request))
    except OrkiExecution.DoesNotExist:
        return HttpResponseBadRequest("RUNTIME_EXECUTION_NOT_FOUND")
    except RuntimeTransitionError as exc:
        return HttpResponseBadRequest(str(exc))
    return JsonResponse(execution_projection(execution))


@login_required
@require_POST
def runtime_execution_pause(
    request: HttpRequest, token: str
) -> JsonResponse | HttpResponseBadRequest:
    return _control(request, token, "pause")


@login_required
@require_POST
def runtime_execution_resume(
    request: HttpRequest, token: str
) -> JsonResponse | HttpResponseBadRequest:
    return _control(request, token, "resume")


@login_required
@require_POST
def runtime_execution_recover(
    request: HttpRequest, token: str
) -> JsonResponse | HttpResponseBadRequest:
    return _control(request, token, "recover")
