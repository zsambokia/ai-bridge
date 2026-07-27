from __future__ import annotations

import os
from pathlib import Path

import pytest

from bridge.settings.environment import load_local_environment


def test_local_environment_loads_values_without_overriding_process_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    environment_file = tmp_path / ".env"
    environment_file.write_text(
        "# local configuration\n"
        "OPENAI_API_KEY=local-test-value\n"
        "export EXTRA_VALUE=ok\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EXTRA_VALUE", "process-value")

    load_local_environment(environment_file)

    assert os.environ["OPENAI_API_KEY"] == "local-test-value"
    assert os.environ["EXTRA_VALUE"] == "process-value"


def test_local_environment_rejects_malformed_entries(tmp_path: Path) -> None:
    environment_file = tmp_path / ".env"
    environment_file.write_text("OPENAI API KEY=value\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid local environment entry"):
        load_local_environment(environment_file)
