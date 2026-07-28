"""Shared Django settings for AI Bridge."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = "development-only-not-a-secret"
DEBUG = False
CLOUDFLARE_TUNNEL_HOSTS = [
    "stage.artificial-software-factory.com",
    "app.artificial-software-factory.com",
]


def _allowed_hosts() -> list[str]:
    """Use explicit host names only; deployment may add, never wildcard, hosts."""
    configured = [
        host.strip()
        for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]
    if "*" in configured:
        raise ValueError("DJANGO_ALLOWED_HOSTS must not contain '*'")
    return list(dict.fromkeys([*CLOUDFLARE_TUNNEL_HOSTS, *configured]))


ALLOWED_HOSTS = _allowed_hosts()
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "projects",
    "storybook.apps.StorybookConfig",
    "confirmationproof.apps.ConfirmationProofConfig",
    "codingproviderproof.apps.CodingProviderProofConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "bridge.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "bridge.wsgi.application"
ASGI_APPLICATION = "bridge.asgi.application"
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "static/"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in CLOUDFLARE_TUNNEL_HOSTS]
MCP_PUBLIC_BASE_URL = os.environ.get(
    "MCP_PUBLIC_BASE_URL", "https://stage.artificial-software-factory.com"
).rstrip("/")
MCP_AUTH_MODE = os.environ.get("MCP_AUTH_MODE", "bearer").strip().lower()
MCP_API_TOKEN = os.environ.get("MCP_API_TOKEN", "")
AI_BRIDGE_DEV_EXECUTION_ACTIVITY = os.environ.get(
    "AI_BRIDGE_DEV_EXECUTION_ACTIVITY", "true"
).strip().lower() in {"1", "true", "yes", "on"}
AI_BRIDGE_HEARTBEAT_ACTIVE_SECONDS = int(
    os.environ.get("AI_BRIDGE_HEARTBEAT_ACTIVE_SECONDS", "60")
)
AI_BRIDGE_HEARTBEAT_WAITING_SECONDS = int(
    os.environ.get("AI_BRIDGE_HEARTBEAT_WAITING_SECONDS", "300")
)
AI_BRIDGE_HEARTBEAT_STALLED_SECONDS = int(
    os.environ.get("AI_BRIDGE_HEARTBEAT_STALLED_SECONDS", "900")
)
