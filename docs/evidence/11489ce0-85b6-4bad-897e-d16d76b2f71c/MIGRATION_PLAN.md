# Migration plan

1. Add independent Conversation, message, state, decision, Context Profile,
   Mission Resolution, and generalized Context Package persistence.
2. Add stateless services for state transitions, profile resolution, adaptive
   policy-constrained context assembly, and Mission Resolution intake.
3. Route Factory Chat only through the Conversation application boundary; do
   not create an execution, invoke a provider, or create a Mission.
4. Converge Article IV and the canonical Conversation diagram with CH-01..15.
5. Add focused acceptance tests, run migrations and all repository release
   gates, publish evidence, AKB and roadmap updates, and bind the result to
   issue #22.

The migration is additive for durable data. Existing legacy Factory/Runtime
tables are not deleted because their records may be evidence, but their
conflicting route is removed from the active Factory Chat flow.
