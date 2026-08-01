# Orki COO mission ownership

Issue #19 makes Orki the active planning owner of Factory Chat.  The browser is
only a Product Owner work surface; it has no provider credential, GitHub
identity, approval authority, or repository-write logic.

```text
Conversation endpoint
  -> Orki server-side model adapter
  -> FactoryMission (durable understanding and sufficiency)
  -> FactoryPlan (durable Product Owner artifact)
  -> one Product Owner approval
  -> server-side RepositoryService
  -> Project Registry and autonomous delivery state
```

`FactoryMission` keeps the objective, users, workflow, inputs, outputs, MVP
boundary, persistence, integrations, costs, risks, assumptions,
recommendations, unresolved decisions, confidence and lifecycle.  Provider
reasoning can enrich it, but requirement sufficiency is calculated and stored
by the server so the plan transition is auditable and cannot loop forever.

The right-side mission projection maps lifecycle values to Hungarian,
Product-Owner-facing language.  Raw enum values are not part of the default
Factory Chat UI.  Desktop uses a fixed projects panel, a fixed mission panel,
and a fixed multiline composer; only the message list scrolls.

After one approval, repository creation is idempotent and server-owned.  The
service authenticates with the configured server environment, checks for
conflicts before creation, bootstraps an empty target, verifies `main`, and
links the resulting repository to the canonical Project Registry.  It refuses
an owner mismatch, conflicting registry value, conflicting workspace remote,
unsafe name, or incomplete proposal rather than overwriting anything.
