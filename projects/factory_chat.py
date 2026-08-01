"""Server-rendered Factory Chat control surface.

This is a projection layer only.  It never issues provider requests or changes
scope, approval, execution, or knowledge authority.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .factory_coding import coding_projection
from .factory_memory import memory_projection
from .factory_planning import approve_plan, create_plan
from .knowledge import review_candidate
from .models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionRun,
    FactoryPlan,
    KnowledgeContextPackage,
    Project,
)

SESSION_KEY = "factory_chat"
VALID_MODES = {"planning", "coding", "memory"}
VALID_PANELS = {"context", "chat", "projects"}


def _planning_response(request: HttpRequest, project: Project) -> HttpResponse:
    """Keep enhanced planning posts on the current page when JavaScript is on.

    The redirect remains a non-JavaScript fallback.  The request header is a
    presentation hint only and never changes server-side authority.
    """
    if request.headers.get("X-Requested-With") == "FactoryChat":
        response = HttpResponse(status=204)
        response["X-Factory-Context"] = reverse("factory-chat-status")
        return response
    return redirect(
        f"{reverse('factory-chat')}?project={project.project_id}&mode=planning"
    )


def _memory_response(request: HttpRequest, project: Project) -> HttpResponse:
    if request.headers.get("X-Requested-With") == "FactoryChat":
        response = HttpResponse(status=204)
        response["X-Factory-Context"] = reverse("factory-chat-status")
        return response
    return redirect(
        f"{reverse('factory-chat')}?project={project.project_id}&mode=memory"
    )


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


def _context(
    project: Project | None, mode: str = "planning", memory_query: str = ""
) -> dict[str, object]:
    if project is None:
        return {
            "project": None,
            "scope": None,
            "roadmap": None,
            "run": None,
            "memory": None,
            "conversation": None,
            "artifact": None,
            "coding": None,
            "memory_mode": None,
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
        "plan": FactoryPlan.objects.filter(project=project)
        .order_by("-created_at")
        .first(),
    }
    if mode == "coding" and context["run"]:
        context["artifact"] = context["run"]
    elif mode == "memory" and context["memory"]:
        context["artifact"] = context["memory"]
    else:
        context["artifact"] = context["scope"] or context["roadmap"]
    run = context["run"]
    context["coding"] = coding_projection(run) if mode == "coding" and isinstance(
        run, ExecutionRun
    ) else coding_projection(None) if mode == "coding" else None
    context["memory_mode"] = (
        memory_projection(project, memory_query) if mode == "memory" else None
    )
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
            "context": _context(project, mode, str(state.get("memory_query", ""))),
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
@require_http_methods(["POST"])
def factory_plan_create(request: HttpRequest) -> HttpResponse:
    project = get_object_or_404(
        Project,
        project_id=request.POST.get("project_id"),
        lifecycle=Project.Lifecycle.ACTIVE,
    )
    try:
        create_plan(
            project,
            {
                "outcome": request.POST.get("outcome", ""),
                "title": request.POST.get("title", ""),
                "kind": request.POST.get("kind", "WORK_ITEM"),
                "task_type": request.POST.get("task_type", "FEATURE"),
                "technical_constraints": request.POST.get("technical_constraints", ""),
                "acceptance_checks": request.POST.get("acceptance_checks", ""),
                "risk_modifiers": request.POST.get("risk_modifiers", ""),
                "business_escalation": request.POST.get("business_escalation", ""),
            },
            request.user.get_username(),
        )
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return _planning_response(request, project)


@login_required
@require_http_methods(["POST"])
def factory_plan_approve(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        approve_plan(plan.pk, plan.project, request.user.get_username())
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return _planning_response(request, plan.project)


@login_required
@require_http_methods(["POST"])
def factory_memory_search(request: HttpRequest) -> HttpResponse:
    project = get_object_or_404(
        Project,
        project_id=request.POST.get("project_id"),
        lifecycle=Project.Lifecycle.ACTIVE,
    )
    query = request.POST.get("query", "").strip()
    if len(query) > 500:
        return HttpResponseBadRequest(
            "A Memory search may contain at most 500 characters."
        )
    state = _state(request)
    state["memory_query"] = query
    request.session.modified = True
    return _memory_response(request, project)


@login_required
@require_http_methods(["POST"])
def factory_memory_review(request: HttpRequest, entry_id: int) -> HttpResponse:
    project = get_object_or_404(
        Project,
        project_id=request.POST.get("project_id"),
        lifecycle=Project.Lifecycle.ACTIVE,
    )
    try:
        review_candidate(
            project,
            entry_id,
            request.POST.get("decision", ""),
            request.user.get_username(),
            request.POST.get("approval_reference", "").strip(),
        )
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return _memory_response(request, project)


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
                str(_state(request).get("memory_query", "")),
            )
        },
    )


@login_required
@require_http_methods(["GET"])
def factory_chat_new_project(request: HttpRequest) -> HttpResponse:
    """Start at the existing governed registry, never a browser-owned record."""
    return render(request, "projects/factory_new_project.html")
