"""Local development settings for AI Bridge."""

from __future__ import annotations

import os
from pathlib import Path

from .environment import load_local_environment

load_local_environment(Path(__file__).resolve().parent.parent.parent / ".env")

# Local conversational MCP acceptance tests use the existing runtime bearer
# setting. Keeping the test-only name in the ignored local .env file avoids
# placing a development credential in tracked configuration, while an
# explicitly configured MCP_API_TOKEN always takes precedence.
if not os.environ.get("MCP_API_TOKEN") and os.environ.get("MCP_TEST_API_TOKEN"):
    os.environ["MCP_API_TOKEN"] = os.environ["MCP_TEST_API_TOKEN"]

from .base import *  # noqa: E402, F403

DEBUG = True

# The local development server is deliberately reached through loopback in the
# browser and in end-to-end tests.  Production host allow-listing remains in
# the base settings; these entries only complete the local profile.
ALLOWED_HOSTS = [*ALLOWED_HOSTS, "localhost", "127.0.0.1", "[::1]"]  # noqa: F405
