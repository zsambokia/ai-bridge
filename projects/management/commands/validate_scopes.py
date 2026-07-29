from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from projects.models import ExecutableScope, ExecutionContract
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
                published_hash = scope.record.get("published_content_hash")
                legacy_hashes = {scope.content_hash}
                if not published_hash and scope.status in {
                    ExecutableScope.Status.COMPLETED,
                    ExecutableScope.Status.ACCEPTED,
                    ExecutableScope.Status.CANCELLED,
                    ExecutableScope.Status.SUPERSEDED,
                }:
                    # Legacy terminal records predate ``published_content_hash``.
                    # Their issued contract is append-only and therefore retains
                    # the authoritative approved-document binding.
                    for contract in ExecutionContract.objects.filter(
                        project=scope.project,
                        approved_sprint_path=scope.published_path,
                    ).order_by("-created_at"):
                        approved = contract.payload.get("approved_scope", {})
                        if approved.get("identifier") == scope.identifier:
                            contract_hash = approved.get("content_hash")
                            if contract_hash:
                                legacy_hashes.add(contract_hash)
                if published_hash:
                    valid_hashes = {published_hash}
                else:
                    valid_hashes = legacy_hashes
                if parsed.get("content_hash") not in valid_hashes:
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
