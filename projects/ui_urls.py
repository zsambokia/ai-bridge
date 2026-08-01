from django.urls import path

from .factory_chat import (
    factory_chat,
    factory_chat_message,
    factory_chat_new_project,
    factory_chat_status,
)

urlpatterns = [
    path("", factory_chat, name="factory-chat"),
    path("factory/message/", factory_chat_message, name="factory-chat-message"),
    path("factory/status/", factory_chat_status, name="factory-chat-status"),
    path(
        "factory/new-project/",
        factory_chat_new_project,
        name="factory-chat-new-project",
    ),
]
