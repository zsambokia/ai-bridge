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
    factory_plan_request_changes,
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
]
