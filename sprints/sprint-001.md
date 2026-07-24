# Sprint 001 — Minimal ChatGPT to Codex Bridge

## Goal

Deliver the smallest working version of AI Bridge that can support this flow:

```text
ChatGPT creates a sprint specification
        ↓
The sprint Markdown file is committed to GitHub
        ↓
ChatGPT starts Codex
        ↓
Codex receives the sprint and the required project Markdown files as context
```

The sprint must not introduce additional platform concepts, workflow abstractions, databases, dashboards, release systems, or generalized orchestration.

## User scenario

The user writes in ChatGPT:

> Create Sprint 1 for the selected software project and start Codex.

AI Bridge must then:

1. create or update the requested sprint Markdown file in the target GitHub repository;
2. identify the required context files declared for that repository;
3. start a Codex task for the target repository;
4. instruct Codex to read the sprint file and every required context file before implementation.

## Scope

### 1. Minimal MCP server

Create an MCP server that exposes exactly these tools:

#### `write_sprint`

Writes a sprint Markdown document to a GitHub repository.

Required inputs:

- repository owner and name;
- target branch;
- sprint file path;
- complete Markdown content;
- commit message.

Expected result:

- the file is created or updated in GitHub;
- the tool returns the repository, branch, file path, and resulting commit SHA.

#### `start_codex`

Starts Codex for a repository and sprint.

Required inputs:

- repository owner and name;
- target branch or commit;
- sprint file path;
- list of Markdown context file paths;
- implementation instruction.

Expected behavior:

- Codex is started against the requested repository state;
- the generated Codex instruction explicitly requires reading every supplied context file before modifying code;
- the sprint file is included in the required context;
- the tool returns the Codex task or execution identifier and its initial status.

Do not add generic task, workflow, memory, project, agent, execution, or orchestration abstractions beyond what is technically required to implement these two tools.

### 2. GitHub integration

The MCP server must use GitHub as the source of truth for sprint and context documents.

Support:

- reading existing UTF-8 Markdown files;
- creating a new sprint file;
- updating an existing sprint file using its current GitHub blob SHA;
- targeting an existing branch;
- returning clear errors when the repository, branch, or context file does not exist.

The implementation must not introduce a separate document database or duplicate GitHub content locally as persistent project memory.

### 3. Context manifest

Use one small repository-level configuration file:

```text
.ai-bridge.json
```

Supported structure:

```json
{
  "context_files": [
    "AGENTS.md",
    "docs/constitution.md",
    "docs/product-vision.md",
    "docs/architecture.md"
  ]
}
```

Rules:

- keep this schema limited to `context_files` in Sprint 001;
- `start_codex` may receive an explicit context file list;
- when no explicit list is supplied, it should read `.ai-bridge.json` from the target repository;
- the sprint file must always be added to the final context list;
- fail before starting Codex when a required file is missing;
- do not add profiles, inheritance, document categories, priorities, versions, environments, or conditional context selection.

### 4. Codex instruction

The instruction sent to Codex must be deterministic and include:

- repository and branch or commit;
- sprint file path;
- complete ordered context file list;
- a requirement to read all listed files before implementation;
- the implementation instruction supplied by ChatGPT;
- a requirement to work only within the sprint scope;
- a requirement to report changed files and tests executed when finished.

A suitable generated instruction format is:

```text
Implement the sprint defined in: sprints/sprint-001.md

Before making any code changes, read these files in order:
1. AGENTS.md
2. docs/constitution.md
3. docs/product-vision.md
4. docs/architecture.md
5. sprints/sprint-001.md

Follow all instructions and constraints found in those files.
Do not implement work outside the sprint scope.

When finished, report:
- changed files;
- tests or checks executed;
- any unresolved issue that prevented completion.
```

The exact transport used to start Codex may follow the simplest officially supported approach available to the implementation environment. Keep that integration behind the `start_codex` tool and document the selected approach in the README.

### 5. Minimal repository documentation

Create:

```text
README.md
AGENTS.md
.ai-bridge.json.example
```

The README must explain only:

- what AI Bridge does;
- the two MCP tools;
- required configuration and credentials;
- how to run the MCP server;
- how to connect it to ChatGPT;
- how `start_codex` obtains and passes context;
- one end-to-end example.

`AGENTS.md` must state that this repository is intentionally minimal and that contributors must not introduce abstractions or features outside the current sprint.

## Out of scope

Sprint 001 must not implement:

- a web UI or dashboard;
- a database;
- custom project memory;
- document versioning outside Git history;
- a release gate;
- automated repair loops;
- pull request approval or merging;
- issue or backlog management;
- generic workflows;
- agent, employee, role, capability, department, meeting, or initiative models;
- support for multiple coding agents;
- automatic sprint generation by the MCP server;
- background status monitoring beyond returning the Codex task identifier and initial status.

## Acceptance criteria

Sprint 001 is complete only when all of the following are demonstrated:

1. The MCP server starts locally using documented commands.
2. ChatGPT can discover the `write_sprint` and `start_codex` tools through MCP.
3. `write_sprint` creates a Markdown sprint file in a test GitHub repository.
4. `write_sprint` can update the same file without creating a duplicate.
5. `start_codex` reads the explicit context list or `.ai-bridge.json`.
6. `start_codex` verifies that every required context file exists.
7. The sprint file is always included in Codex context.
8. Codex is successfully started for the repository.
9. The Codex task instruction contains the ordered file list and the requirement to read it before implementation.
10. The tool returns a usable Codex task or execution identifier.
11. Automated tests cover context resolution, missing-file failure, sprint creation, sprint update, and Codex instruction generation.
12. No out-of-scope abstraction or feature is added.

## Required proof

The implementation pull request or final report must include:

- the exact command used to start the MCP server;
- the MCP tool discovery output showing both tools;
- a link or path to the test sprint committed through `write_sprint`;
- the generated Codex instruction with secrets removed;
- the returned Codex task or execution identifier;
- automated test output;
- a list of changed files.

## Definition of done

Sprint 001 is done when this sequence works without manual copying between ChatGPT and Codex:

```text
ChatGPT
  → write_sprint
  → GitHub sprint Markdown
  → start_codex
  → Codex starts with the required Markdown context
```

Nothing beyond this sequence is required for the first release.