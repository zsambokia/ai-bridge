import assert from "node:assert/strict";
import test from "node:test";
import { GitHubClient } from "../src/github.js";
import { resolveContext } from "../src/context.js";
import { buildCodexInstruction, startCodex } from "../src/codex.js";
import { createHandlers } from "../src/server.js";

function mockGithub(files = {}) {
  return {
    token: "token",
    writes: [],
    async getFile(_owner, _repo, _ref, path) {
      if (!(path in files)) throw new Error(`GitHub request failed (404) for ${path}: Not Found`);
      return { path, sha: "sha", content: files[path] };
    },
    async fileExists(_owner, _repo, _ref, path) { return path in files; },
    async writeFile(input) { this.writes.push(input); return { repository: `${input.owner}/${input.repo}`, branch: input.branch, path: input.path, commit_sha: "commit-sha" }; },
  };
}

test("resolves explicit context and appends sprint exactly once", async () => {
  const github = mockGithub({ "AGENTS.md": "rules", "docs/architecture.md": "architecture", "sprints/sprint-001.md": "sprint" });
  assert.deepEqual(await resolveContext({ github, owner: "o", repo: "r", ref: "main", sprintPath: "sprints/sprint-001.md", contextFiles: ["AGENTS.md", "sprints/sprint-001.md", "docs/architecture.md"] }), ["AGENTS.md", "docs/architecture.md", "sprints/sprint-001.md"]);
});

test("resolves context from the manifest", async () => {
  const github = mockGithub({ ".ai-bridge.json": '{"context_files":["AGENTS.md"]}', "AGENTS.md": "rules", "sprints/sprint-001.md": "sprint" });
  assert.deepEqual(await resolveContext({ github, owner: "o", repo: "r", ref: "main", sprintPath: "sprints/sprint-001.md" }), ["AGENTS.md", "sprints/sprint-001.md"]);
});

test("fails before Codex launch when a context file is missing", async () => {
  const github = mockGithub({ "sprints/sprint-001.md": "sprint" });
  await assert.rejects(() => resolveContext({ github, owner: "o", repo: "r", ref: "main", sprintPath: "sprints/sprint-001.md", contextFiles: ["AGENTS.md"] }), /AGENTS.md/);
});

test("write_sprint sends a creation without a blob SHA", async () => {
  const calls = [];
  const fetchImpl = async (_url, options = {}) => { calls.push(options); const payload = options.method === "PUT" ? { commit: { sha: "commit" } } : { object: { sha: "branch" } }; return new Response(JSON.stringify(payload), { status: 200 }); };
  const client = new GitHubClient({ token: "token", fetchImpl });
  client.getFile = async () => { throw new Error("GitHub request failed (404): Not Found"); };
  const result = await client.writeFile({ owner: "o", repo: "r", branch: "main", path: "sprints/s.md", content: "# Sprint", message: "add" });
  assert.equal(JSON.parse(calls.at(-1).body).sha, undefined);
  assert.equal(result.commit_sha, "commit");
});

test("write_sprint sends the current blob SHA when updating", async () => {
  const calls = [];
  const fetchImpl = async (_url, options = {}) => { calls.push(options); const payload = options.method === "PUT" ? { commit: { sha: "commit" } } : { object: { sha: "branch" } }; return new Response(JSON.stringify(payload), { status: 200 }); };
  const client = new GitHubClient({ token: "token", fetchImpl });
  client.getFile = async () => ({ sha: "current-blob" });
  await client.writeFile({ owner: "o", repo: "r", branch: "main", path: "sprints/s.md", content: "# Updated", message: "update" });
  assert.equal(JSON.parse(calls.at(-1).body).sha, "current-blob");
});

test("generates deterministic Codex instruction with ordered files", () => {
  const instruction = buildCodexInstruction({ owner: "o", repo: "r", ref: "main", sprintPath: "sprints/sprint-001.md", contextFiles: ["AGENTS.md", "sprints/sprint-001.md"], implementationInstruction: "Implement it." });
  assert.match(instruction, /Repository: o\/r\nRevision: main/);
  assert.match(instruction, /1\. AGENTS\.md\n2\. sprints\/sprint-001\.md/);
  assert.match(instruction, /Before making any code changes, read these files in order:/);
  assert.match(instruction, /Do not implement work outside the sprint scope/);
});

test("start_codex returns the launch identifier and instruction", async () => {
  const github = mockGithub({ "AGENTS.md": "rules", "sprints/sprint-001.md": "sprint" });
  const handlers = createHandlers({ github, launchCodex: async ({ instruction }) => ({ task_id: "42", status: "started", captured: instruction }) });
  const result = await handlers.start_codex({ owner: "o", repository: "r", ref: "main", sprint_file_path: "sprints/sprint-001.md", context_files: ["AGENTS.md"], implementation_instruction: "Implement it." });
  assert.equal(result.task_id, "42");
  assert.match(result.instruction, /1\. AGENTS\.md/);
});


test("startCodex checks out the requested revision and launches Codex", async () => {
  const commands = [];
  const task = await startCodex({
    owner: "o", repo: "r", ref: "abc123", instruction: "Read the sprint.", token: "secret",
    runImpl: async (command, args, options) => { commands.push({ command, args, options }); },
    spawnImpl: () => ({ pid: 1234, unref() {} }),
  });
  assert.deepEqual(task, { task_id: "1234", status: "started" });
  assert.deepEqual(commands.map(({ command, args }) => [command, args[0]]), [["git", "clone"], ["git", "-C"], ["git", "-C"]]);
  assert.deepEqual(commands[1].args.slice(-2), ["origin", "abc123"]);
  assert.equal(commands[0].options.env.GIT_CONFIG_KEY_0, "http.extraHeader");
  assert.equal(commands[0].options.env.GIT_CONFIG_VALUE_0, "AUTHORIZATION: bearer secret");
});
