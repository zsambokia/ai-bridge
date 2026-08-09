"""Plain-language Product Owner projection for the Factory Chat.

The browser is intentionally a conversation and review surface.  Canonical
Project, plan, approval, execution and knowledge services retain authority.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID, uuid4

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from .factory_coding import coding_projection
from .factory_memory import memory_projection
from .factory_missions import human_projection, mission_for
from .factory_orki import availability, get_or_create_session, messages_for
from .factory_planning import (
    approve_plan,
    reject_plan,
    request_plan_changes,
)
from .factory_workspace import approval_projection, cognitive_workspace_projection
from .github_repository_provider import GitHubRepositoryProvider
from .knowledge import review_candidate
from .models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionProvider,
    ExecutionRun,
    FactoryChatMessage,
    FactoryChatSession,
    FactoryPlan,
    GovernanceApproval,
    KnowledgeContextPackage,
    OrkiExecution,
    Project,
    RepositoryKnowledgeReceipt,
    RuntimeDeployment,
)
from .orki_runtime import (
    create_factory_plan_in_shadow,
    dispatch_factory_chat_execution,
    execution_projection,
    observe_factory_plan_approval,
    start_factory_chat_execution,
)
from .repository_lifecycle import RepositoryBootstrapLifecycle

SESSION_KEY = "factory_chat"
MAX_MESSAGE_LENGTH = 12_000
VALID_MODES = {"planning", "coding", "memory"}
VALID_PANELS = {"context", "chat", "projects"}
logger = logging.getLogger(__name__)


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


def _plain_run_state(run: ExecutionRun | None) -> str:
    if run is None:
        return "Még nincs elindított fejlesztés."
    if run.lifecycle == ExecutionRun.Lifecycle.CANCELLED:
        return "Az előző futás biztonságosan leállt."
    if run.lifecycle == ExecutionRun.Lifecycle.REQUESTED:
        return "A fejlesztés indulásra vár."
    if run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT:
        return "A fejlesztési folyamat megállt, mert további információ szükséges."
    projection = coding_projection(run)
    classification = projection.get("classification", {})
    if isinstance(classification, dict):
        return str(classification.get("detail", "A fejlesztés állapota frissül."))
    return "A fejlesztés állapota frissül."


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
            "plan": None,
            "deployment": None,
            "runtime": None,
            "state_text": "Válassz vagy indíts egy projektet.",
            "next_step": "Mondd el, min szeretnél dolgozni.",
        }
    run = (
        ExecutionRun.objects.filter(contract__project=project)
        .order_by("-updated_at")
        .first()
    )
    deployment = (
        RuntimeDeployment.objects.filter(delivery__run__contract__project=project)
        .order_by("-updated_at")
        .first()
    )
    session = (
        FactoryChatSession.objects.filter(project=project)
        .order_by("-updated_at")
        .first()
    )
    mission_object = mission_for(session) if session is not None else None
    runtime_execution = (
        OrkiExecution.objects.filter(plan__goal__project=project)
        .select_related("plan__goal")
        .order_by("-created_at")
        .first()
    )
    context: dict[str, object] = {
        "project": project,
        "scope": project.scopes.exclude(status=ExecutableScope.Status.ACCEPTED)
        .order_by("-updated_at")
        .first(),
        "roadmap": project.roadmap_items.order_by("-updated_at").first(),
        "run": run,
        "memory": KnowledgeContextPackage.objects.filter(project=project)
        .order_by("-created_at")
        .first(),
        "conversation": ConversationOrchestration.objects.filter(scope__project=project)
        .order_by("-updated_at")
        .first(),
        "plan": FactoryPlan.objects.filter(project=project)
        .order_by("-created_at")
        .first(),
        "deployment": deployment,
        "mission": human_projection(mission_object),
        "runtime": execution_projection(runtime_execution)
        if runtime_execution is not None
        else None,
        # Read-only Workspace projections.  The browser never owns or mutates
        # repository, roadmap, or AKB records.
        "roadmap_items": project.roadmap_items.order_by("item_key")[:20],
        "repository_receipts": RepositoryKnowledgeReceipt.objects.filter(
            project=project
        ).order_by("-updated_at")[:20],
    }
    context["artifact"] = (
        run
        if mode == "coding" and run
        else context["memory"]
        if mode == "memory"
        else context["scope"] or context["roadmap"]
    )
    context["coding"] = coding_projection(run) if mode == "coding" and run else None
    context["memory_mode"] = (
        memory_projection(project, memory_query) if mode == "memory" else None
    )
    plan = context["plan"]
    workspace = cognitive_workspace_projection(
        project, mission_object, plan if isinstance(plan, FactoryPlan) else None
    )
    context["workspace"] = workspace
    context["approval"] = approval_projection(
        workspace, plan if isinstance(plan, FactoryPlan) else None
    )
    context["state_text"] = (
        _plain_run_state(run)
        if mode == "coding"
        else (
            "Jóváhagyásra váró terv van."
            if isinstance(plan, FactoryPlan)
            and plan.status == FactoryPlan.Status.PENDING_APPROVAL
            else "A következő lépést közösen pontosítjuk."
        )
    )
    context["next_step"] = (
        "Nézd át és hagyd jóvá a tervet."
        if isinstance(plan, FactoryPlan)
        and plan.status == FactoryPlan.Status.PENDING_APPROVAL
        else "Írd le röviden, mire van szükséged."
    )
    return context


def _enhanced(request: HttpRequest) -> bool:
    return request.headers.get("X-Requested-With") == "FactoryChat"


def _request_correlation(request: HttpRequest) -> str:
    """Use the browser retry key when it is safe; never reflect arbitrary text."""
    candidate = request.POST.get("request_id", "").strip()
    try:
        return str(uuid4() if not candidate else UUID(candidate))
    except (AttributeError, ValueError):
        return str(uuid4())


def _safe_chat_error(
    request: HttpRequest,
    *,
    correlation_id: str,
    code: str = "RUNTIME_INGRESS_REJECTED",
    status: int = 400,
    message: str | None = None,
) -> HttpResponse:
    """Return only a plain-language recovery path to the Product Owner."""
    message = message or (
        "A Runtime a kérést nem tudta rögzíteni; javítsd a jelzett adatot, "
        "majd küldd el újra."
    )
    if _enhanced(request):
        return JsonResponse(
            {
                "ok": False,
                "error": {"code": code, "message": message, "retryable": True},
                "correlation_id": correlation_id,
            },
            status=status,
        )
    return HttpResponseBadRequest(message)


def _safe_action_error(request: HttpRequest, error: ValueError) -> HttpResponse:
    """Do not expose internal validation tokens through plan or memory controls."""
    logger.warning(
        "factory_chat_action_failed", extra={"factory_reason": type(error).__name__}
    )
    message = (
        "Ezt a műveletet most nem lehet befejezni. "
        "Frissítsd az állapotot, majd próbáld újra."
    )
    if _enhanced(request):
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "ACTION_UNAVAILABLE",
                    "message": message,
                    "retryable": True,
                },
            },
            status=400,
        )
    return HttpResponseBadRequest(message)


def _response(request: HttpRequest, project: Project, mode: str) -> HttpResponse:
    if _enhanced(request):
        response = HttpResponse(status=204)
        response["X-Factory-Context"] = reverse("factory-chat-status")
        return response
    return redirect(
        f"{reverse('factory-chat')}?project={project.project_id}&mode={mode}"
    )


def _continue_after_plan_approval(plan: FactoryPlan, actor: str) -> FactoryPlan:
    """Record one plan approval without starting repository or execution work."""
    approved_plan = approve_plan(plan.pk, plan.project, actor)
    observe_factory_plan_approval(approved_plan, actor=actor)
    session = (
        FactoryChatSession.objects.filter(project=plan.project)
        .order_by("-updated_at")
        .first()
    )
    if session:
        mission = mission_for(session)
        mission.phase = mission.Phase.PLAN_APPROVED
        mission.delivery_status = {
            "state": "execution_preparation",
            "next": (
                "A jóváhagyott terv és a dokumentum-projekciók elkészültek. "
                "A végrehajtás külön, kanonikus szerződés alapján indítható."
            ),
        }
        mission.save(update_fields=["phase", "delivery_status", "updated_at"])
    return approved_plan


def _new_project_from_answers(answers: list[str]) -> Project:
    name = answers[0] or "Új projekt"
    base = slugify(name) or "uj-projekt"
    project_id = base
    suffix = 2
    while Project.objects.filter(project_id=project_id).exists():
        project_id = f"{base}-{suffix}"
        suffix += 1
    return Project.objects.create(
        project_id=project_id,
        display_name=name,
        repository_full_name=f"pending/{project_id}",
        definition_path=f"projects/{project_id}.yaml",
        lifecycle=Project.Lifecycle.ACTIVE,
        onboarding_status=Project.OnboardingStatus.PENDING,
        onboarding_reason=(
            "A projekt indítási adatai rögzítve vannak; "
            "a fejlesztési környezet előkészítése következik."
        ),
    )


@login_required
@require_http_methods(["GET"])
def factory_chat(request: HttpRequest) -> HttpResponse:
    state = _state(request)
    mode = request.GET.get("mode", str(state.get("mode", "planning"))).lower()
    panel = request.GET.get("panel", str(state.get("panel", "chat"))).lower()
    mode = mode if mode in VALID_MODES else "planning"
    panel = panel if panel in VALID_PANELS else "chat"
    state.update({"mode": mode, "panel": panel})
    request.session.modified = True
    project = _selected_project(request)
    orki_session = get_or_create_session(request, project)
    return render(
        request,
        "projects/factory_chat.html",
        {
            "projects": Project.objects.filter(lifecycle=Project.Lifecycle.ACTIVE),
            "context": _context(project, mode, str(state.get("memory_query", ""))),
            "mode": mode,
            "panel": panel,
            "workspace_navigation": (
                ("home", "Home"), ("orki", "Orki"), ("projects", "Projects"),
                ("knowledge", "Knowledge"), ("repository", "Repository"),
                ("execution", "Execution"), ("roadmap", "Roadmap"),
                ("decisions", "Decisions"), ("runtime", "Runtime"),
                ("evidence", "Evidence"), ("administration", "Administration"),
            ),
            # A generous display window keeps a long working conversation useful,
            # while the transcript remains separate from canonical memory/state.
            "messages": messages_for(orki_session)[-100:],
            "orki_availability": availability(orki_session),
        },
    )


@login_required
@require_POST
def workspace_repository_action(request: HttpRequest) -> JsonResponse:
    """Invoke repository intake only through its canonical lifecycle owner."""
    project = _selected_project(request)
    if project is None:
        return JsonResponse(
            {"ok": False, "error": {"code": "PROJECT_REQUIRED"}}, status=409
        )
    approval_reference = request.POST.get("approval_reference", "").strip()
    if not approval_reference:
        return JsonResponse(
            {"ok": False, "error": {"code": "APPROVAL_REFERENCE_REQUIRED"}},
            status=400,
        )
    provider = ExecutionProvider.objects.filter(
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        enabled=True,
    ).first()
    if provider is None:
        return JsonResponse(
            {"ok": False, "error": {"code": "REPOSITORY_PROVIDER_UNAVAILABLE"}},
            status=409,
        )
    action = request.POST.get("action", "")
    lifecycle = RepositoryBootstrapLifecycle(GitHubRepositoryProvider(provider))
    try:
        if action == "bootstrap":
            mode = request.POST.get("mode", "import")
            receipts = lifecycle.bootstrap(
                project,
                mode=mode,
                actor=request.user.get_username(),
                approval_reference=approval_reference,
            )
        elif action in {"sync", "reindex"}:
            receipt = project.repository_knowledge_receipts.first()
            if receipt is None:
                raise ValueError("REPOSITORY_BASELINE_REQUIRED")
            # Reindex is deliberately an incremental lifecycle refresh.  The
            # Workspace must not touch AKB or the vector store directly.
            receipts = lifecycle.sync(
                project,
                commit_sha=receipt.source_version,
                actor=request.user.get_username(),
                approval_reference=approval_reference,
            )
        else:
            raise ValueError("REPOSITORY_ACTION_INVALID")
    except ValueError as exc:
        return JsonResponse(
            {"ok": False, "error": {"code": str(exc)}}, status=409
        )
    return JsonResponse(
        {
            "ok": True,
            "action": action,
            "receipts": [
                {
                    "path": receipt.source_path,
                    "version": receipt.source_version,
                    "status": receipt.status,
                    "classification": receipt.classification,
                }
                for receipt in receipts
            ],
        }
    )


@login_required
@require_http_methods(["POST"])
def factory_chat_message(request: HttpRequest) -> HttpResponse:
    # Preserve multiline input exactly; reject only whitespace-only submissions.
    text = request.POST.get("message", "")
    correlation_id = _request_correlation(request)
    if not text.strip() or len(text) > MAX_MESSAGE_LENGTH:
        return _safe_chat_error(
            request,
            correlation_id=correlation_id,
            code="MESSAGE_INVALID",
            status=400,
            message="Az üzenet megadása kötelező és legfeljebb 12 000 karakter lehet.",
        )
    project = _selected_project(request)
    if project is None:
        return _safe_chat_error(
            request,
            correlation_id=correlation_id,
            code="PROJECT_REQUIRED",
            status=400,
            message="A Runtime indításához előbb válassz vagy hozz létre projektet.",
        )
    execution: OrkiExecution | None = None
    try:
        execution = start_factory_chat_execution(
            project=project,
            session=get_or_create_session(request, project),
            text=text,
            correlation_id=correlation_id,
            actor=request.user.get_username(),
        )
        # Existing clients retain their synchronous response shape, but the
        # work is still exclusively executed by the Runtime.  The Live Runtime
        # Monitor explicitly opts into the two-step ingress/stream contract.
        runtime_async = request.headers.get("X-Orki-Runtime-Async") == "1"
        if not runtime_async:
            dispatch_factory_chat_execution(
                str(execution.token), actor=request.user.get_username()
            )
    except (OSError, TimeoutError, ValueError, RuntimeError) as exc:
        logger.warning(
            "factory_chat_request_failed",
            extra={
                "factory_correlation_id": correlation_id,
                "factory_reason": type(exc).__name__,
                "factory_provider_id": "",
                "factory_latency_ms": None,
                "factory_state_id": project.project_id if project else "",
                "factory_conversation_id": "",
            },
        )
        if execution is not None:
            execution.refresh_from_db()
            projection = execution_projection(execution)
            if _enhanced(request):
                return JsonResponse(
                    {
                        "ok": False,
                        "error": {
                            "code": "RUNTIME_STATE_REQUIRES_ATTENTION",
                            "message": projection["human_message"],
                            "retryable": execution.state.startswith("WAITING_"),
                        },
                        "correlation_id": correlation_id,
                        "execution": projection,
                        "orki_availability": availability(
                            get_or_create_session(request, project)
                        ),
                    },
                    status=409,
                )
            return HttpResponseBadRequest(str(projection["human_message"]))
        return _safe_chat_error(
            request,
            correlation_id=correlation_id,
            code="RUNTIME_INGRESS_FAILED",
            status=500,
            message=(
                "A Runtime indítása a kérés rögzítése előtt megszakadt. "
                "Kérlek, próbáld meg ismét."
            ),
        )
    if _enhanced(request):
        execution.refresh_from_db()
        orki_session = get_or_create_session(request, project)
        payload = {
            "messages": [
                message
                for message in messages_for(orki_session)
                if message.get("correlation_id") == correlation_id
            ],
            "ok": True,
            "orki_availability": availability(orki_session),
            "correlation_id": correlation_id,
            "execution": execution_projection(execution),
        }
        if runtime_async:
            payload["dispatch_url"] = reverse(
                "runtime-execution-dispatch", args=[execution.token]
            )
        return JsonResponse(payload, status=202 if runtime_async else 200)
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
        create_factory_plan_in_shadow(
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
            actor=request.user.get_username(),
            session=(
                FactoryChatSession.objects.filter(project=project)
                .order_by("-updated_at")
                .first()
            ),
        )
    except ValueError as exc:
        return _safe_action_error(request, exc)
    return _response(request, project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_approve(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        _continue_after_plan_approval(plan, request.user.get_username())
    except ValueError as exc:
        return _safe_action_error(request, exc)
    return _response(request, plan.project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_request_changes(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        request_plan_changes(plan.pk, plan.project, request.POST.get("reason", ""))
    except ValueError as exc:
        return _safe_action_error(request, exc)
    return _response(request, plan.project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_reject(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        reject_plan(plan.pk, plan.project, request.POST.get("reason", ""))
    except ValueError as exc:
        return _safe_action_error(request, exc)
    return _response(request, plan.project, "planning")


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
        return HttpResponseBadRequest("A keresés legfeljebb 500 karakter lehet.")
    _state(request)["memory_query"] = query
    request.session.modified = True
    return _response(request, project, "memory")


@login_required
@require_http_methods(["POST"])
def factory_memory_review(request: HttpRequest, entry_id: int) -> HttpResponse:
    project = get_object_or_404(
        Project,
        project_id=request.POST.get("project_id"),
        lifecycle=Project.Lifecycle.ACTIVE,
    )
    try:
        decision = request.POST.get("decision", "")
        approval_reference = ""
        if decision == "APPROVE":
            approval_reference = f"factory-memory:{uuid4()}"
            GovernanceApproval.objects.create(
                reference=approval_reference,
                project=project,
                approved_action="akb.review_candidate",
                approved_by=request.user.get_username(),
            )
        review_candidate(
            project, entry_id, decision, request.user.get_username(), approval_reference
        )
    except ValueError as exc:
        return _safe_action_error(request, exc)
    return _response(request, project, "memory")


@login_required
@require_http_methods(["GET"])
def factory_chat_status(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "projects/factory_context_status.html",
        {
            "context": _context(
                _selected_project(request),
                str(_state(request).get("mode", "planning")),
                str(_state(request).get("memory_query", "")),
            ),
            "orki_availability": availability(
                get_or_create_session(request, _selected_project(request))
            ),
        },
    )


@login_required
@require_http_methods(["POST", "GET"])
def factory_chat_new_project(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        project = _new_project_from_answers(["\u00daj projekt"])
        state = _state(request)
        state.update({"project_id": project.project_id, "mode": "planning"})
        request.session.modified = True
        session = get_or_create_session(request, project)
        FactoryChatMessage.objects.create(
            session=session,
            role=FactoryChatMessage.Role.ORKI,
            body=(
                "Kezdjük el. Egy mondatban mondd el, milyen eredményt "
                "szeretnél elérni; én összerakom az első javaslatot és jelzem, "
                "ha valódi döntésre lesz szükség."
            ),
        )
        messages = messages_for(session)
        if _enhanced(request):
            orki_session = get_or_create_session(request, project)
            return JsonResponse(
                {
                    "messages": messages,
                    "ok": messages[-1]["status"] != FactoryChatMessage.Status.FAILED,
                    "orki_availability": availability(orki_session),
                    "project": {"id": project.project_id, "name": project.display_name},
                }
            )
        return redirect(
            f"{reverse('factory-chat')}?project={project.project_id}&panel=chat&mode=planning"
        )
    return redirect(f"{reverse('factory-chat')}?panel=chat&mode=planning")
