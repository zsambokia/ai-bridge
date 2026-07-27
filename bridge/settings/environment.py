"""Local-only environment-file support without adding a runtime dependency."""

from __future__ import annotations

import os
import re
from pathlib import Path

_ENVIRONMENT_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_local_environment(path: Path) -> None:
    """Load simple ``KEY=VALUE`` pairs while preserving process environment.

    The file is intentionally optional and is used only by local settings.
    Deployment environments supply secrets through their secret manager instead.
    """
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not _ENVIRONMENT_KEY.fullmatch(key):
            raise ValueError(f"Invalid local environment entry: {key or raw_line!r}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
