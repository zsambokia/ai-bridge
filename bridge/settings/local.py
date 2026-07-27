"""Local development settings for AI Bridge."""

from __future__ import annotations

from pathlib import Path

from .environment import load_local_environment

load_local_environment(Path(__file__).resolve().parent.parent.parent / ".env")

from .base import *  # noqa: E402, F403

DEBUG = True
