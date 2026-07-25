#!/usr/bin/env node
import readline from "node:readline";
import { GitHubClient } from "./github.js";
import { resolveContext } from "./context.js";
import { buildCodexInstruction, startCodex } from "./codex.js";

const TOOL_DEFINITIONS = [
  {
    name: "write_sprint",
    description: "Create or update a complete sprint Markdown document in a GitHub repository.",
    inputSchema: { type: "object", additionalProperties: false, required: ["owner", "repository", "branch", "sprint_file_path", "markdown", "commit_message"], properties: {
      owner: { type: "string" }, repository: { type: "string" }, branch: { type: "string" }, sprint_file_path: { type: "string" }, markdown: { type: "string" }, commit_message: { type: "string" },
    } },
  },
  {
    name: "start_codex",
    description: "Start Codex against a GitHub revision after verifying its required Markdown context.",
    inputSchema: { type: "object", additionalProperties: false, required: ["owner", "repository", "ref", "sprint_file_path", "implementation_instruction"], properties: {
      owner: { type: "string" }, repository: { type: "string" }, ref: { type: "string", description: "Branch name or commit SHA." }, sprint_file_path: { type: "string" }, context_files: { type: "array", items: { type: "string" } }, implementation_instruction: { type: "string" },
    } },
  },
];

function requireStrings(args, names) {
  for (const name of names) if (typeof args[name] !== "string" || !args[name]) throw new Error(`${name} is required.`);
}
function toolResponse(data) { return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }], structuredContent: data }; }

export function createHandlers({ github = new GitHubClient({ token: process.env.GITHUB_TOKEN }), launchCodex = startCodex } = {}) {
  return {
    async write_sprint(args) {
      requireStrings(args, ["owner", "repository", "branch", "sprint_file_path", "markdown", "commit_message"]);
      if (!args.sprint_file_path.endsWith(".md")) throw new Error("sprint_file_path must be a Markdown (.md) file path.");
      return github.writeFile({ owner: args.owner, repo: args.repository, branch: args.branch, path: args.sprint_file_path, content: args.markdown, message: args.commit_message });
    },
    async start_codex(args) {
      requireStrings(args, ["owner", "repository", "ref", "sprint_file_path", "implementation_instruction"]);
      const contextFiles = await resolveContext({ github, owner: args.owner, repo: args.repository, ref: args.ref, sprintPath: args.sprint_file_path, contextFiles: args.context_files });
      const instruction = buildCodexInstruction({ owner: args.owner, repo: args.repository, ref: args.ref, sprintPath: args.sprint_file_path, contextFiles, implementationInstruction: args.implementation_instruction });
      const task = await launchCodex({ owner: args.owner, repo: args.repository, ref: args.ref, instruction, token: github.token });
      return { ...task, instruction };
    },
  };
}

export function startServer(input = process.stdin, output = process.stdout) {
  const handlers = createHandlers();
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  rl.on("line", async (line) => {
    let request;
    try {
      request = JSON.parse(line);
      let result;
      if (request.method === "initialize") result = { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "ai-bridge", version: "0.1.0" } };
      else if (request.method === "tools/list") result = { tools: TOOL_DEFINITIONS };
      else if (request.method === "tools/call") {
        const handler = handlers[request.params?.name];
        if (!handler) throw new Error(`Unknown tool: ${request.params?.name}`);
        result = toolResponse(await handler(request.params.arguments || {}));
      } else if (request.method?.startsWith("notifications/")) return;
      else throw new Error(`Unsupported method: ${request.method}`);
      if (request.id !== undefined) output.write(`${JSON.stringify({ jsonrpc: "2.0", id: request.id, result })}\n`);
    } catch (error) {
      if (request?.id !== undefined) output.write(`${JSON.stringify({ jsonrpc: "2.0", id: request.id, error: { code: -32000, message: error.message } })}\n`);
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) startServer();
