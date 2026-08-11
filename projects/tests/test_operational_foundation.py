from __future__ import annotations

import inspect

from django.test import SimpleTestCase

from projects import (
    execution,
    factory_chat,
    orki_runtime,
    provider_gateway,
    workflow_engine,
)
from projects.models import ExecutionJob


class OperationalFoundationTests(SimpleTestCase):
    def test_execution_job_is_the_single_operational_queue_and_worker_lifecycle(
        self,
    ) -> None:
        model_source = inspect.getsource(__import__("projects.models", fromlist=["*"]))
        execution_source = inspect.getsource(execution)
        self.assertIn("class ExecutionJob", model_source)
        self.assertNotIn("class OperationalWorkItem", model_source)
        self.assertIn("def claim_next_job", execution_source)
        self.assertIn("def heartbeat_job", execution_source)
        self.assertIn("def execute_claimed_job", execution_source)
        self.assertTrue(ExecutionJob._meta.get_field("lease_owner"))

    def test_runtime_and_workflow_cannot_reach_provider_implementations(self) -> None:
        runtime_source = inspect.getsource(orki_runtime)
        workflow_source = inspect.getsource(workflow_engine)

        self.assertNotIn("from .providers", runtime_source)
        self.assertNotIn("from .providers", workflow_source)
        self.assertNotIn("execute_chat_provider_task", workflow_source)
        self.assertNotIn("enqueue_work_item", runtime_source)
        self.assertNotIn("OperationalWorkItem", runtime_source)
        self.assertIn("invoke_factory_chat_model", runtime_source)

    def test_provider_gateway_has_no_conversation_or_mission_dependency(self) -> None:
        """Provider code receives domain semantics; it never imports their owners."""
        gateway_source = inspect.getsource(provider_gateway)

        self.assertNotIn("from .factory_orki", gateway_source)
        self.assertNotIn("from .factory_missions", gateway_source)
        self.assertIn("context_builder", gateway_source)
        self.assertIn("prompt_builder", gateway_source)
        self.assertIn("response_decoder", gateway_source)

    def test_conversation_surface_delegates_user_interaction_to_conversation_boundary(
        self,
    ) -> None:
        """The chat surface is an adapter, not a Runtime or repository owner."""
        source = inspect.getsource(factory_chat)

        for symbol in (
            "start_factory_chat_execution",
            "dispatch_factory_chat_execution",
            "observe_factory_plan_approval",
            "create_factory_plan_in_shadow",
            "RepositoryBootstrapLifecycle",
            "GitHubRepositoryProvider",
        ):
            self.assertNotIn(symbol, source)

        for symbol in ("conversation_for", "record_message"):
            self.assertIn(symbol, source)
