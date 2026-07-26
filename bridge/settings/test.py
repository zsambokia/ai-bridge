"""Test settings for AI Bridge."""

from __future__ import annotations

from .base import *  # noqa: F403

ALLOWED_HOSTS = ["testserver", *CLOUDFLARE_TUNNEL_HOSTS]  # noqa: F405
