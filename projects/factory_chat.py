"""Server-rendered Factory Chat control surface.

This is a projection layer only.  It never issues provider requests or changes
scope, approval, execution, or knowledge authority.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionRun,
    KnowledgeContextPackage,
    Project,
)

SESSION_KEY = "factory_chat"
VALID_MODES = {"planning", "coding", "memory"}
VALID_PANELS = {"context", "chat", "projects"}


def _state(request: HttpRequest) -> dict[str, Any]:
    return request.session.setdefault(SESSION_KEY, {"messages": []})


def _selected_project(request: HttpRequest) -> Project | None:
    projects = Project.objects.filter(lifecycle=Project.Lifecycle.ACTIVE)
    requested = request.GET.get("project") or _state(request).get("project_id")
    project = (
        projects.filter(project_id=requested).first() if requested else projects.first()
    )
    if project:
        state = _state(request)
        state["project_id"] = project.project_id
        request.session.modified = True
    return project


def _context(project: Project | None, mode: str = "planning") -> dict[str, object]:
    if project is None:
        return {
            "project": None,
            "scope": None,
            "roadmap": None,
            "run": None,
            "memory": None,
            "conversation": None,
            "artifact": None,
        }
    context: dict[str, object] = {
        "project": project,
        "scope": project.scopes.exclude(status=ExecutableScope.Status.ACCEPTED)
        .order_by("-updated_at")
        .first(),
        "roadmap": project.roadmap_items.order_by("-updated_at").first(),
        "run": ExecutionRun.objects.filter(contract__project=project)
        .order_by("-updated_at")
        .first(),
        "memory": KnowledgeContextPackage.objects.filter(project=project)
        .order_by("-created_at")
        .first(),
        "conversation": ConversationOrchestration.objects.filter(scope__project=project)
        .order_by("-updated_at")
        .first(),
    }
    if mode == "coding" and context["run"]:
        context["artifact"] = context["run"]
    elif mode == "memory" and context["memory"]:
        context["artifact"] = context["memory"]
    else:
        context["artifact"] = context["scope"] or context["roadmap"]
    return context


@login_required
@require_http_methods(["GET"])
def factory_chat(request: HttpRequest) -> HttpResponse:
    state = _state(request)
    mode = request.GET.get("mode", str(state.get("mode", "planning"))).lower()
    panel = request.GET.get("panel", str(state.get("panel", "context"))).lower()
    if mode not in VALID_MODES:
        mode = "planning"
    if panel not in VALID_PANELS:
        panel = "context"
    state.update({"mode": mode, "panel": panel})
    request.session.modified = True
    project = _selected_project(request)
    return render(
        request,
        "projects/factory_chat.html",
        {
            "projects": Project.objects.filter(lifecycle=Project.Lifecycle.ACTIVE),
            "context": _context(project, mode),
            "mode": mode,
            "panel": panel,
            "messages": state.get("messages", [])[-20:],
        },
    )


@login_required
@require_http_methods(["POST"])
def factory_chat_message(request: HttpRequest) -> HttpResponse:
    text = request.POST.get("message", "").strip()
    if not text or len(text) > 1000:
        return HttpResponseBadRequest(
            "Az üzenet megadása kötelező és legfeljebb 1000 karakter lehet."
        )
    state = _state(request)
    messages = list(state.get("messages", []))[-18:]
    messages.extend(
        [
            {"role": "owner", "text": text},
            {
                "role": "bridge",
                "text": (
                    "Az üzenet rögzítve. Válasszon egy kanonikus "
                    "munkakörnyezetet vagy jóváhagyási kártyát; a böngésző "
                    "nem indít közvetlen szolgáltatói műveletet."
                ),
            },
        ]
    )
    state["messages"] = messages
    request.session.modified = True
    return redirect("factory-chat")


@login_required
@require_http_methods(["GET"])
def factory_chat_status(request: HttpRequest) -> HttpResponse:
    """Return only the server-owned Active Work Context projection.

    The browser may refresh this fragment, but it cannot create, approve, or
    execute work through it.
    """
    return render(
        request,
        "projects/factory_context_status.html",
        {
            "context": _context(
                _selected_project(request),
                str(_state(request).get("mode", "planning")),
            )
        },
    )


@login_required
@require_http_methods(["GET"])
def factory_chat_new_project(request: HttpRequest) -> HttpResponse:
    """Start at the existing governed registry, never a browser-owned record."""
    return render(request, "projects/factory_new_project.html")
