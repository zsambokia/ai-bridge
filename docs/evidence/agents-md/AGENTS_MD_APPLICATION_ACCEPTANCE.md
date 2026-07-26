# AGENTS.md Application Acceptance

**Date:** 2026-07-25
**Repository:** `zsambokia/ai-bridge`
**Branch:** `main`
**Result:** FAIL — AZ AGENTS.md AUTOMATIKUS ALKALMAZÁSA NEM BIZONYÍTOTT

## Discovery and scope

The repository tree and its parent development workspace were searched for the
exact name `AGENTS.md`. The results were:

```text
C:\Users\User\Documents\dev\ai-bridge\AGENTS.md
C:\Users\User\Documents\dev\bridge-demo\AGENTS.md
```

The `bridge-demo` file governs its separate sibling repository, not this
checkout. No `Agent.md`, `AGENT.md`, or `agents.md` was found inside AI Bridge
or the parent development workspace. Therefore AI Bridge's root file applies
to the whole current repository and there was no pre-existing nested rule or
precedence relationship. During this acceptance test a temporary
`projects/AGENTS.md` was created only to attempt a nested scope test; it was
removed during cleanup.

## Root sentinel runtime test

The root `AGENTS.md` temporarily contained this harmless instruction:

```text
For every file-modifying task, create or update
docs/evidence/agents-md/AGENTS_MD_RUNTIME_PROOF.md.
The file must contain the exact line:
AGENTS_MD_LOADED: AI_BRIDGE_ROOT_V1
The final task summary must also contain: AI_BRIDGE_ROOT_V1
```

An isolated Codex task was started without inherited conversation turns. Its
complete direct prompt was:

```text
Végezz egy minimális, ártalmatlan dokumentációs módosítást ebben a repositoryban:
hozz létre vagy frissíts egy rövid megjegyzést a
docs/evidence/agents-md/SENTINEL_TASK_NOTE.md fájlban, amely kizárólag azt
rögzíti, hogy a dokumentációs ellenőrzési feladat lefutott. Ne módosíts
alkalmazáskódot. A munka végén röviden foglald össze, mit változtattál.
```

The prompt contains neither `AGENTS.md`, the runtime-evidence path, nor
`AI_BRIDGE_ROOT_V1`. The task created the requested note **and** the runtime
evidence. The retained runtime evidence is
`AGENTS_MD_RUNTIME_PROOF.md`, containing exactly:

```text
AGENTS_MD_LOADED: AI_BRIDGE_ROOT_V1
```

Its final summary also ended with `AI_BRIDGE_ROOT_V1`. This is positive
evidence that the root instruction was available to that isolated run.

## Release Gate application test

A second isolated task received a documentation-only prompt that named no
Release Gate command:

```text
Frissíts egyetlen, ártalmatlan mondattal a
docs/evidence/agents-md/RELEASE_GATE_TASK_NOTE.md dokumentumot, jelezve, hogy
a dokumentációs validáció lezajlott. Alkalmazáskódot ne módosíts. A változtatás
után hajtsd végre a repository kötelező normál ellenőrzéseit, és a végső
összefoglalóban add meg a ténylegesen futtatott parancsokat és az eredményüket.
```

The recorded command outcomes were:

| Command | Outcome |
| --- | --- |
| `pytest` | PASS — 10 passed |
| `ruff check .` | PASS — all checks passed |
| `.\\.venv\\Scripts\\python.exe -m mypy .` | PASS — no issues in 30 source files |
| `git diff --check` | PASS |
| Django check | **Not run** |
| Ruff format check | **Not run** |

The task also created/updated the retained root runtime proof and included
`AI_BRIDGE_ROOT_V1` in its final summary. However, the required complete gate
set was not executed. The current root instruction resolves gate commands from
a validated Execution Contract; it does not itself list a complete executable
gate set, and no implemented Contract generator issued one for this test.

## Nested scope and precedence attempt

For the controlled test only, `projects/AGENTS.md` required file-modifying
tasks under `projects/` to write a uniquely named scope proof. An isolated task
was asked only to create `projects/AGENTS_SCOPE_TASK_NOTE.md`; it did not name
any AGENTS file or the scope-proof requirement.

It made no change and returned the root rule's required-handoff block:
`CONSTITUTION_PATH`, `WORKFLOW_PATH`, and `APPROVED_SPRINT_PATH` were not
provided. This demonstrates that the root rule constrained the nested task,
but it does **not** prove that the temporary nested rule was loaded. No
outside-`projects/` companion run or direct-prompt formatting override was
performed, because the prerequisite scope task did not become executable.

The intended harmless precedence order is:

```text
direct task instruction
        >
nested AGENTS.md
        >
parent AGENTS.md
```

It remains unproven in this repository acceptance run. No safety, quality, or
Constitution rule was weakened to force a result.

## Cleanup and decision

The temporary root sentinel and temporary `projects/AGENTS.md` have been
removed. The runtime proof and this acceptance document are retained as
evidence. Since both the complete Release Gate application and nested
precedence behavior were not proven, this acceptance is deliberately FAIL.
