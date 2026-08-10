---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Project Registry and Context Foundation

Sprint 003 establishes one runtime Project Registry model (`projects.Project`)
and one runtime Project Context model (`projects.ProjectContext`). There are no
parallel Registry, onboarding, or Context models.

The static Project Definition is loaded only from `.bridge/project.yaml`. The
loader validates its structure and rejects runtime lifecycle, onboarding,
Context, and capability state. The bootstrap service derives readiness from the
definition, repository identity, governance documents, Release Gate command
resolution, configured execution branch, and an approved Sprint.

```text
static .bridge/project.yaml
             |
             v
canonical definition loader
             |
             v
projects.Project (PENDING | READY | INVALID)
             |
             v
projects.ProjectContext (VALID | INVALID | STALE)
```

`bootstrap_project` is the one constrained `BOOTSTRAP` operation. It upserts a
single Registry record, creates the first Context only for a `READY` Project,
and is idempotent once that Context is valid. All values are resolved from the
selected definition and Registry record; no project-name or repository-specific
branch exists in platform code.
