"""Tests for read-only Project Registry administration."""

from __future__ import annotations

from django.contrib import admin
from django.test import RequestFactory

from projects.models import ExecutionProvider, ExecutionRun, Project, ProjectContext


def test_project_registry_admin_is_registered_and_read_only() -> None:
    request = RequestFactory().get("/admin/projects/project/")
    project_admin = admin.site._registry[Project]
    context_admin = admin.site._registry[ProjectContext]

    assert project_admin.has_add_permission(request) is False
    assert project_admin.has_change_permission(request) is False
    assert project_admin.has_delete_permission(request) is False
    assert context_admin.has_add_permission(request) is False
    assert context_admin.has_change_permission(request) is False
    assert context_admin.has_delete_permission(request) is False


def test_execution_provider_admin_list_excludes_sensitive_configuration() -> None:
    provider_admin = admin.site._registry[ExecutionProvider]

    assert "configuration" not in provider_admin.list_display
    assert "credential_binding" not in provider_admin.list_display
    assert "related_openai_provider" in provider_admin.list_display
    assert "authentication_mode" in provider_admin.list_display
    assert "configuration_status" in provider_admin.list_display
    assert "coding_capability" in provider_admin.list_display


def test_execution_run_admin_shows_run_id_as_first_data_column() -> None:
    run_admin = admin.site._registry[ExecutionRun]

    assert run_admin.list_display[0] == "run_id"
    assert getattr(run_admin, "run_id").short_description == "Run ID"
