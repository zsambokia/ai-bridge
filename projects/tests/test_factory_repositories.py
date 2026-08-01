from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from projects.factory_repositories import (
    RepositoryRemediationRequired,
    ensure_repository,
)
from projects.models import FactoryChatSession, FactoryMission, Project


class FactoryRepositoryServiceTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_user(username="repository-owner")
        self.project = Project.objects.create(
            project_id="repository-service-test",
            display_name="Repository service test",
            repository_full_name="pending/repository-service-test",
            definition_path="projects/repository-service-test.yaml",
        )
        session = FactoryChatSession.objects.create(
            project=self.project, actor_identity=user.username
        )
        self.mission = FactoryMission.objects.create(
            session=session,
            repository_proposal={
                "mode": "create",
                "owner": "repository-owner",
                "name": "issue19-disposable",
                "visibility": "private",
                "description": "Issue 19 disposable proof",
            },
        )

    def test_create_is_registered_and_retries_without_another_create(self) -> None:
        with (
            patch(
                "projects.factory_repositories._github_identity",
                return_value="repository-owner",
            ),
            patch(
                "projects.factory_repositories.subprocess.run",
                side_effect=[
                    SimpleNamespace(returncode=1),
                    SimpleNamespace(returncode=0),
                ],
            ),
            patch("projects.factory_repositories._run", return_value="") as run,
            patch(
                "projects.factory_repositories._bootstrap_git", return_value="abc123"
            ),
        ):
            first = ensure_repository(self.mission)
            second = ensure_repository(self.mission)
        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(first.initial_commit, "abc123")
        self.project.refresh_from_db()
        self.assertEqual(
            self.project.repository_full_name, "repository-owner/issue19-disposable"
        )
        self.mission.refresh_from_db()
        self.assertEqual(self.mission.delivery_status["initial_commit"], "abc123")
        self.assertEqual(
            sum(
                call.args[:3] == ("gh", "repo", "create") for call in run.call_args_list
            ),
            1,
        )

    def test_registry_conflict_stops_before_github_mutation(self) -> None:
        self.project.repository_full_name = "other/owned-project"
        self.project.save(update_fields=["repository_full_name"])
        with patch("projects.factory_repositories._run") as run:
            with self.assertRaises(RepositoryRemediationRequired):
                ensure_repository(self.mission)
        run.assert_not_called()
