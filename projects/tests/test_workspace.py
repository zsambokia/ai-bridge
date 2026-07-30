"""Isolated workspace repository-binding tests."""

import stat
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from projects import workspace
from projects.models import ExecutionRun


def test_command_label_does_not_include_command_arguments() -> None:
    assert workspace._command_label(
        ["git", "clone", "https://token@example.invalid/private.git"]
    ) == "git:clone"
    assert workspace._command_label(["git", "-C", "workspace", "checkout"]) == (
        "git:checkout"
    )
    assert workspace._command_label(["python.exe", "-m", "venv", "workspace"]) == (
        "python:venv"
    )


def test_target_repository_url_uses_registered_project_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target_root = tmp_path / "bridge-demo"
    target_root.mkdir()
    run = SimpleNamespace(
        contract=SimpleNamespace(project=SimpleNamespace()),
        repository="zsambokia/bridge-demo",
    )
    observed_command: list[str] = []
    monkeypatch.setattr(
        workspace, "project_repository_root", lambda *_: target_root
    )
    monkeypatch.setattr(
        workspace, "_repository_identity", lambda _: "zsambokia/bridge-demo"
    )

    def fake_run(command: list[str], **_: object) -> str:
        observed_command.extend(command)
        return "https://github.com/zsambokia/bridge-demo.git"

    monkeypatch.setattr(workspace, "_run", fake_run)

    assert workspace._target_repository_url(cast(ExecutionRun, run)) == (
        "https://github.com/zsambokia/bridge-demo.git"
    )
    assert observed_command == [
        "git",
        "-C",
        str(target_root),
        "remote",
        "get-url",
        "origin",
    ]


def test_set_repository_remote_adds_or_updates_the_named_remote(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> str:
        commands.append(command)
        return "origin\n" if command[-1] == "remote" else ""

    monkeypatch.setattr(workspace, "_run", fake_run)

    workspace._set_repository_remote(
        tmp_path, "workspace-cache", "C:/workspace-cache/target.git"
    )
    workspace._set_repository_remote(
        tmp_path, "origin", "https://github.com/zsambokia/bridge-demo.git"
    )

    assert commands[1][-3:] == [
        "add",
        "workspace-cache",
        "C:/workspace-cache/target.git",
    ]
    assert commands[3][-3:] == [
        "set-url",
        "origin",
        "https://github.com/zsambokia/bridge-demo.git",
    ]


@pytest.mark.parametrize(
    ("filenames", "expected"),
    [([], False), (["pyproject.toml"], True), (["setup.py"], True)],
)
def test_installable_python_project_detection(
    tmp_path: Path, filenames: list[str], expected: bool
) -> None:
    for filename in filenames:
        (tmp_path / filename).write_text("", encoding="utf-8")

    assert workspace._is_installable_python_project(tmp_path) is expected


def test_target_repository_url_rejects_repository_binding_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    run = SimpleNamespace(
        contract=SimpleNamespace(project=SimpleNamespace()),
        repository="zsambokia/bridge-demo",
    )
    monkeypatch.setattr(workspace, "project_repository_root", lambda *_: tmp_path)
    monkeypatch.setattr(
        workspace, "_repository_identity", lambda _: "zsambokia/ai-bridge"
    )

    with pytest.raises(
        workspace.WorkspaceError, match="WORKSPACE_REPOSITORY_BINDING_MISMATCH"
    ):
        workspace._target_repository_url(cast(ExecutionRun, run))


def test_mismatched_workspace_repository_is_removed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace_root = tmp_path / "workspace"
    repository = workspace_root / "repository"
    repository.mkdir(parents=True)
    (repository / "stale.txt").write_text("stale", encoding="utf-8")
    monkeypatch.setattr(
        workspace,
        "_run",
        lambda *_args, **_kwargs: "https://github.com/zsambokia/ai-bridge.git",
    )

    workspace._discard_mismatched_workspace_repository(
        repository,
        workspace_root,
        "https://github.com/zsambokia/bridge-demo.git",
    )

    assert not repository.exists()


def test_mismatched_readonly_workspace_repository_is_removed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace_root = tmp_path / "workspace"
    repository = workspace_root / "repository"
    repository.mkdir(parents=True)
    readonly_file = repository / "readonly.txt"
    readonly_file.write_text("stale", encoding="utf-8")
    readonly_file.chmod(stat.S_IREAD)
    monkeypatch.setattr(
        workspace,
        "_run",
        lambda *_args, **_kwargs: "https://github.com/zsambokia/ai-bridge.git",
    )

    workspace._discard_mismatched_workspace_repository(
        repository,
        workspace_root,
        "https://github.com/zsambokia/bridge-demo.git",
    )

    assert not repository.exists()


def test_matching_workspace_repository_is_reused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace_root = tmp_path / "workspace"
    repository = workspace_root / "repository"
    repository.mkdir(parents=True)
    monkeypatch.setattr(
        workspace,
        "_run",
        lambda *_args, **_kwargs: "https://github.com/zsambokia/bridge-demo.git",
    )

    workspace._discard_mismatched_workspace_repository(
        repository,
        workspace_root,
        "https://github.com/zsambokia/bridge-demo.git",
    )

    assert repository.is_dir()


def test_mismatched_repository_cache_is_removed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cache_root = tmp_path / "cache"
    mirror = cache_root / "target.git"
    mirror.mkdir(parents=True)
    monkeypatch.setattr(
        workspace,
        "_run",
        lambda *_args, **_kwargs: "https://github.com/zsambokia/ai-bridge.git",
    )

    workspace._discard_mismatched_workspace_repository(
        mirror,
        cache_root,
        "https://github.com/zsambokia/bridge-demo.git",
    )

    assert not mirror.exists()
