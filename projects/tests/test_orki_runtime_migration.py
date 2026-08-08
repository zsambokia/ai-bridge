from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class OrkiRuntimeMigrationTests(TransactionTestCase):
    """Prove the additive Runtime migration can be rolled back and reapplied."""

    def test_runtime_foundation_migration_round_trip(self) -> None:
        executor = MigrationExecutor(connection)
        before_runtime = [("projects", "0054_operational_reasoning_engine_state")]
        runtime_foundation = [("projects", "0056_orkiexecution_waiting_for_user")]

        executor.migrate(before_runtime)
        executor = MigrationExecutor(connection)
        executor.migrate(runtime_foundation)
        self.assertIn("projects_orkiexecution", connection.introspection.table_names())

        executor = MigrationExecutor(connection)
        executor.migrate(before_runtime)
        self.assertNotIn(
            "projects_orkiexecution", connection.introspection.table_names()
        )

        executor = MigrationExecutor(connection)
        executor.migrate(runtime_foundation)
        self.assertIn("projects_orkiexecution", connection.introspection.table_names())
