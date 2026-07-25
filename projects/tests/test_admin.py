"""Tests for read-only Project Registry administration."""

from __future__ import annotations

from django.contrib import admin
from django.test import RequestFactory

from projects.models import Project, ProjectContext


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
