from django.urls import path

from .factory_chat import (
    factory_chat,
    factory_chat_message,
    factory_chat_new_project,
    factory_chat_status,
    factory_memory_review,
    factory_memory_search,
    factory_plan_approve,
    factory_plan_create,
    factory_plan_reject,
    factory_plan_request_changes,
)
from .runtime_api import (
    runtime_execution_detail,
    runtime_execution_dispatch,
    runtime_execution_event_stream,
    runtime_execution_pause,
    runtime_execution_recover,
    runtime_execution_resume,
)

urlpatterns = [
    path("", factory_chat, name="factory-chat"),
    path("factory/message/", factory_chat_message, name="factory-chat-message"),
    path("factory/plan/", factory_plan_create, name="factory-plan-create"),
    path(
        "factory/plans/<int:plan_id>/approve/",
        factory_plan_approve,
        name="factory-plan-approve",
    ),
    path(
        "factory/plans/<int:plan_id>/changes/",
        factory_plan_request_changes,
        name="factory-plan-request-changes",
    ),
    path(
        "factory/plans/<int:plan_id>/reject/",
        factory_plan_reject,
        name="factory-plan-reject",
    ),
    path("factory/status/", factory_chat_status, name="factory-chat-status"),
    path("factory/memory/search/", factory_memory_search, name="factory-memory-search"),
    path(
        "factory/memory/<int:entry_id>/review/",
        factory_memory_review,
        name="factory-memory-review",
    ),
    path(
        "factory/new-project/",
        factory_chat_new_project,
        name="factory-chat-new-project",
    ),
    path(
        "runtime/executions/<uuid:token>/",
        runtime_execution_detail,
        name="runtime-execution-detail",
    ),
    path(
        "runtime/executions/<uuid:token>/dispatch/",
        runtime_execution_dispatch,
        name="runtime-execution-dispatch",
    ),
    path(
        "runtime/executions/<uuid:token>/events/stream/",
        runtime_execution_event_stream,
        name="runtime-execution-event-stream",
    ),
    path(
        "runtime/executions/<uuid:token>/pause/",
        runtime_execution_pause,
        name="runtime-execution-pause",
    ),
    path(
        "runtime/executions/<uuid:token>/resume/",
        runtime_execution_resume,
        name="runtime-execution-resume",
    ),
    path(
        "runtime/executions/<uuid:token>/recover/",
        runtime_execution_recover,
        name="runtime-execution-recover",
    ),
]
