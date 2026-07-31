"""Test settings for AI Bridge."""

from __future__ import annotations

import hashlib

from .base import *  # noqa: F403

ALLOWED_HOSTS = ["testserver", *CLOUDFLARE_TUNNEL_HOSTS]  # noqa: F405
MCP_AUTH_MODE = "bearer"
MCP_API_TOKEN = "test-mcp-token"
MCP_PRODUCT_OWNER_CALLER_FINGERPRINTS = (
    hashlib.sha256(b"Bearer test-mcp-token").hexdigest(),
)
