# AI Bridge

AI Bridge is a deliberately small [MCP](https://modelcontextprotocol.io/) server. It lets ChatGPT commit a sprint Markdown document to GitHub and then start the Codex CLI with that sprint and the repository's required Markdown context.

It implements only two tools:

- `write_sprint` creates or updates one Markdown sprint file through GitHub's Contents API. Its inputs are `owner`, `repository`, `branch`, `sprint_file_path`, `markdown`, and `commit_message`; its result includes the repository, branch, file path, and commit SHA.
- `start_codex` verifies context files in GitHub and starts `codex exec` in a fresh temporary clone. Its inputs are `owner`, `repository`, `ref` (a branch or commit SHA), `sprint_file_path`, optional `context_files`, and `implementation_instruction`.

## Requirements and configuration

- Node.js 20 or newer.
- Git installed and available on `PATH` (used to clone the requested repository revision).
- The `codex` CLI installed and authenticated on the machine that runs the MCP server.
- `GITHUB_TOKEN` set to a token that can read the target repository and write sprint files. The token is also used for the temporary clone created for Codex.
- An existing target branch.

For default context resolution, copy `.ai-bridge.json.example` to `.ai-bridge.json` **in the target GitHub repository** and keep only its `context_files` array. Every listed path must be an existing UTF-8 Markdown file. Instead, ChatGPT may pass `context_files` explicitly. In either case, the sprint file is appended as the final required context file and every file is checked in GitHub before Codex starts.

## Run locally

```bash
export GITHUB_TOKEN=github_pat_...
npm start
```

The exact MCP server command is `npm start`. The server uses stdio and writes JSON-RPC responses only to stdout.

## Connect to ChatGPT

Add this local MCP server in a ChatGPT client that supports local stdio MCP servers, using the command below and providing `GITHUB_TOKEN` in that client's environment:

```json
{
  "mcpServers": {
    "ai-bridge": {
      "command": "npm",
      "args": ["start"],
      "cwd": "/path/to/ai-bridge"
    }
  }
}
```

After connecting, tool discovery (`tools/list`) returns exactly `write_sprint` and `start_codex`.

## End-to-end example

First ask ChatGPT to call `write_sprint`:

```json
{
  "owner": "acme",
  "repository": "example-app",
  "branch": "main",
  "sprint_file_path": "sprints/sprint-001.md",
  "markdown": "# Sprint 001\n\nImplement the requested change.",
  "commit_message": "docs: add Sprint 001"
}
```

Then ask it to call `start_codex` with the returned branch and sprint path:

```json
{
  "owner": "acme",
  "repository": "example-app",
  "ref": "main",
  "sprint_file_path": "sprints/sprint-001.md",
  "context_files": ["AGENTS.md", "docs/architecture.md"],
  "implementation_instruction": "Implement Sprint 001 completely."
}
```

`start_codex` validates the three ordered files (`AGENTS.md`, `docs/architecture.md`, and the sprint), generates an instruction that requires Codex to read them before changing code, clones the requested GitHub revision into a temporary directory, and returns its process ID with initial status `started`.
