"""Run the mandatory backend release checks in a fixed order."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence


def run(command: Sequence[str]) -> int:
    """Execute one release-gate command and return its exit status."""
    print(f"$ {' '.join(command)}", flush=True)
    return subprocess.run(command, check=False).returncode


def main() -> int:
    """Run all required checks and stop at the first failure."""
    commands = (
        (sys.executable, "manage.py", "check", "--settings=bridge.settings.local"),
        (sys.executable, "-m", "pytest"),
        (sys.executable, "-m", "ruff", "check", "."),
        (sys.executable, "-m", "ruff", "format", "--check", "."),
        (sys.executable, "-m", "mypy", "."),
    )
    for command in commands:
        if run(command) != 0:
            return 1
    print("Backend Release Gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
