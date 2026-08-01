"""Plain-language Product Owner projection for the Factory Chat.

The browser is intentionally a conversation and review surface.  Canonical
Project, plan, approval, execution and knowledge services retain authority.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from .factory_coding import coding_projection
from .factory_memory import memory_projection
from .factory_missions import begin_autonomous_delivery, human_projection, mission_for
from .factory_orki import availability, get_or_create_session, messages_for
from .factory_orki import reply as orki_reply
from .factory_planning import (
    approve_plan,
    create_plan,
    reject_plan,
    request_plan_changes,
)
from .factory_repositories import RepositoryRemediationRequired, ensure_repository
from .knowledge import review_candidate
from .models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionRun,
    FactoryChatMessage,
    FactoryChatSession,
    FactoryPlan,
    GovernanceApproval,
    KnowledgeContextPackage,
    Project,
    RuntimeDeployment,
)

SESSION_KEY = "factory_chat"
VALID_MODES = {"planning", "coding", "memory"}
VALID_PANELS = {"context", "chat", "projects"}
DISCOVERY_QUESTIONS = (
    "Minek nevezzük ezt a projektet?",
    "Kik fogják használni?",
    "Mi legyen az első, legfontosabb dolog, amit meg tudnak benne csinálni?",
    (
        "Van olyan határidő vagy elvárás, amit mindenképpen tartsunk "
        "szem előtt? (Kihagyható.)"
    ),
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
        "mission": human_projection(
            mission_for(session)
            if (
                session := FactoryChatSession.objects.filter(project=project)
                .order_by("-updated_at")
                .first()
            )
            is not None
            else None
        ),
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


def _response(request: HttpRequest, project: Project, mode: str) -> HttpResponse:
    if _enhanced(request):
        response = HttpResponse(status=204)
        response["X-Factory-Context"] = reverse("factory-chat-status")
        return response
    return redirect(
        f"{reverse('factory-chat')}?project={project.project_id}&mode={mode}"
    )


def _add_messages(
    state: dict[str, Any], *messages: dict[str, str]
) -> list[dict[str, str]]:
    history = list(state.get("messages", []))[-16:]
    history.extend(messages)
    state["messages"] = history
    return list(messages)


def _start_discovery(state: dict[str, Any], kind: str = "plan") -> str:
    state["discovery"] = {"kind": kind, "answers": [], "question": 0}
    return DISCOVERY_QUESTIONS[0]


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


def _finish_discovery(
    request: HttpRequest, state: dict[str, Any], discovery: dict[str, Any]
) -> str:
    answers = [str(answer) for answer in discovery["answers"]]
    project = _selected_project(request)
    if discovery["kind"] == "new_project":
        project = _new_project_from_answers(answers)
        state["project_id"] = project.project_id
        state["mode"] = "planning"
    if project is None:
        return "Előbb indítsunk vagy válasszunk egy projektet."
    outcome = answers[2] if len(answers) > 2 else answers[0]
    title = f"{project.display_name}: első fejlesztési terv"
    create_plan(
        project,
        {
            "outcome": outcome,
            "title": title,
            "technical_constraints": answers[3] if len(answers) > 3 else "",
            "acceptance_checks": "A Product Owner áttekinti a tervet.",
        },
        request.user.get_username(),
    )
    state.pop("discovery", None)
    return (
        "Elkészítettem az első, áttekinthető tervet. A jobb oldalon "
        "egyetlen jóváhagyással folytathatod."
    )


def _reply_to_message(request: HttpRequest, text: str) -> str:
    state = _state(request)
    discovery = state.get("discovery")
    if isinstance(discovery, dict):
        answers = list(discovery.get("answers", []))
        answers.append(text)
        discovery["answers"] = answers
        question = int(discovery.get("question", 0)) + 1
        discovery["question"] = question
        if question < len(DISCOVERY_QUESTIONS):
            return DISCOVERY_QUESTIONS[question]
        return _finish_discovery(request, state, discovery)
    lowered = text.casefold()
    if any(
        token in lowered
        for token in ("új projekt", "uj projekt", "új alkalmazás", "uj alkalmazas")
    ):
        return _start_discovery(state, "new_project")
    if any(
        token in lowered
        for token in (
            "hogyan érhető el",
            "hogyan erheto el",
            "elérhető az alkalmazás",
            "elerheto az alkalmazas",
            "url",
            "preview",
        )
    ):
        project = _selected_project(request)
        deployment = (
            RuntimeDeployment.objects.filter(delivery__run__contract__project=project)
            .order_by("-updated_at")
            .first()
            if project
            else None
        )
        preview = ""
        if deployment and isinstance(deployment.receipt, dict):
            preview = str(
                deployment.receipt.get("url")
                or deployment.receipt.get("preview_url")
                or ""
            )
        url = preview or request.build_absolute_uri(reverse("factory-chat"))
        target = f" A kiválasztott projekt: {project.display_name}." if project else ""
        return f"Az alkalmazás most itt érhető el: {url}.{target}"
    if any(
        token in lowered
        for token in (
            "terv",
            "fejlessz",
            "készíts",
            "keszits",
            "szeretnék",
            "szeretnek",
        )
    ):
        return _start_discovery(state)
    return (
        "Értem. Írd le, milyen eredményt szeretnél, és néhány rövid kérdéssel "
        "közösen összeállítjuk a tervet."
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
            "messages": messages_for(orki_session)[-20:],
            "orki_availability": availability(orki_session),
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
    added = orki_reply(request, _selected_project(request), text)
    if _enhanced(request):
        orki_session = get_or_create_session(request, _selected_project(request))
        return JsonResponse(
            {
                "messages": added,
                "ok": added[-1]["status"] != FactoryChatMessage.Status.FAILED,
                "orki_availability": availability(orki_session),
            }
        )
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
    return _response(request, project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_approve(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        approve_plan(plan.pk, plan.project, request.user.get_username())
        session = (
            FactoryChatSession.objects.filter(project=plan.project)
            .order_by("-updated_at")
            .first()
        )
        if session:
            mission = mission_for(session)
            mission.phase = mission.Phase.PLAN_APPROVED
            mission.save(update_fields=["phase", "updated_at"])
            mission = begin_autonomous_delivery(mission)
            try:
                ensure_repository(mission)
            except RepositoryRemediationRequired as error:
                mission.delivery_status = {
                    "state": "repository_remediation",
                    "next": "Orki biztonságosan javítja a repository előkészítését.",
                    "reason": str(error)[:300],
                }
                mission.save(update_fields=["delivery_status", "updated_at"])
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return _response(request, plan.project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_request_changes(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        request_plan_changes(plan.pk, plan.project, request.POST.get("reason", ""))
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return _response(request, plan.project, "planning")


@login_required
@require_http_methods(["POST"])
def factory_plan_reject(request: HttpRequest, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(FactoryPlan, pk=plan_id)
    try:
        reject_plan(plan.pk, plan.project, request.POST.get("reason", ""))
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
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
        return HttpResponseBadRequest(str(exc))
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
        messages = orki_reply(
            request,
            project,
            "\u00daj projektet szeretn\u00e9k ind\u00edtani. "
            "Vezesd a felfedez\u00e9st, "
            "\u00e9s csak a val\u00f3ban sz\u00fcks\u00e9ges "
            "els\u0151 k\u00e9rd\u00e9st tedd fel.",
        )
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
