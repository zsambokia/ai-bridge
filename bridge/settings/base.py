"""Shared Django settings for AI Bridge."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = "development-only-not-a-secret"
DEBUG = False
ALLOWED_HOSTS: list[str] = []
INSTALLED_APPS = ["core", "projects"]
MIDDLEWARE: list[str] = []
ROOT_URLCONF = "bridge.urls"
TEMPLATES: list[dict[str, object]] = []
WSGI_APPLICATION = "bridge.wsgi.application"
ASGI_APPLICATION = "bridge.asgi.application"
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
