from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from projects.models import ExecutableScope
from projects.scopes import parse_scope_document
from projects.services import project_repository_root


class Command(BaseCommand):
    help = "Validate published canonical scope documents for the current repository."

    def handle(self, *args: Any, **options: Any) -> None:
        default_root = Path.cwd().resolve()
        errors = []
        checked_paths = set()
        for scope in ExecutableScope.objects.exclude(published_path=""):
            try:
                root = project_repository_root(scope.project, default_root)
                if root != default_root:
                    continue
                checked_paths.add((root, scope.published_path))
                parsed = parse_scope_document(
                    (root / scope.published_path).read_text(encoding="utf-8"),
                    scope.project,
                )
                if parsed.get("content_hash") != scope.content_hash:
                    raise ValueError("published content hash differs")
            except (OSError, ValueError) as exc:
                errors.append(f"{scope.identifier}: {exc}")
        for directory in (
            default_root / "docs" / "sprints",
            default_root / "docs" / "work-items",
        ):
            if not directory.is_dir():
                continue
            for path in directory.rglob("*.md"):
                relative_path = path.relative_to(default_root).as_posix()
                if (default_root, relative_path) in checked_paths:
                    continue
                text = path.read_text(encoding="utf-8")
                if text.startswith("---"):
                    try:
                        parse_scope_document(text)
                    except ValueError as exc:
                        errors.append(f"{path}: {exc}")
        if errors:
            raise CommandError("; ".join(errors))
        self.stdout.write(self.style.SUCCESS("All canonical scopes are valid."))
