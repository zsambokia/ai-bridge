import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

export function buildCodexInstruction({ owner, repo, ref, sprintPath, contextFiles, implementationInstruction }) {
  const listed = contextFiles.map((file, index) => `${index + 1}. ${file}`).join("\n");
  return `Repository: ${owner}/${repo}\nRevision: ${ref}\n\nImplement the sprint defined in: ${sprintPath}\n\nBefore making any code changes, read these files in order:\n${listed}\n\nFollow all instructions and constraints found in those files.\nDo not implement work outside the sprint scope.\n\nImplementation instruction:\n${implementationInstruction}\n\nWhen finished, report:\n- changed files;\n- tests or checks executed;\n- any unresolved issue that prevented completion.`;
}

function run(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, options);
    let stderr = "";
    child.stderr?.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => code === 0 ? resolve() : reject(new Error(`${command} failed: ${stderr.trim()}`)));
  });
}

export async function startCodex({ owner, repo, ref, instruction, token, spawnImpl = spawn, runImpl = run }) {
  const directory = await mkdtemp(join(tmpdir(), "ai-bridge-"));
  const remote = `https://github.com/${owner}/${repo}.git`;
  // Git config environment variables keep the token out of process arguments.
  const gitEnvironment = {
    ...process.env,
    GIT_CONFIG_COUNT: "1",
    GIT_CONFIG_KEY_0: "http.extraHeader",
    GIT_CONFIG_VALUE_0: `AUTHORIZATION: bearer ${token}`,
  };
  await runImpl("git", ["clone", "--depth", "1", remote, directory], { stdio: ["ignore", "ignore", "pipe"], env: gitEnvironment });
  await runImpl("git", ["-C", directory, "fetch", "--depth", "1", "origin", ref], { stdio: ["ignore", "ignore", "pipe"], env: gitEnvironment });
  await runImpl("git", ["-C", directory, "checkout", "--detach", "FETCH_HEAD"], { stdio: ["ignore", "ignore", "pipe"] });

  const child = spawnImpl("codex", ["exec", instruction], {
    cwd: directory,
    detached: true,
    stdio: "ignore",
  });
  child.unref();
  if (!child.pid) throw new Error("Codex did not return a process identifier.");
  return { task_id: String(child.pid), status: "started" };
}
