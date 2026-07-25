function validateMarkdownPath(path, label) {
  if (typeof path !== "string" || !path.endsWith(".md")) {
    throw new Error(`${label} must be a Markdown (.md) file path.`);
  }
}

export async function resolveContext({ github, owner, repo, ref, sprintPath, contextFiles }) {
  validateMarkdownPath(sprintPath, "sprint_file_path");
  let declared = contextFiles;
  if (declared === undefined) {
    let manifest;
    try {
      manifest = await github.getFile(owner, repo, ref, ".ai-bridge.json");
    } catch (error) {
      throw new Error(`Could not read .ai-bridge.json: ${error.message}`);
    }
    try {
      declared = JSON.parse(manifest.content).context_files;
    } catch (error) {
      throw new Error(`Invalid .ai-bridge.json: ${error.message}`);
    }
  }
  if (!Array.isArray(declared)) throw new Error("context_files must be an array.");

  const files = [...new Set(declared)];
  for (const path of files) validateMarkdownPath(path, "context_files entry");
  const ordered = [...files.filter((path) => path !== sprintPath), sprintPath];
  const missing = [];
  for (const path of ordered) {
    if (!(await github.fileExists(owner, repo, ref, path))) missing.push(path);
  }
  if (missing.length) throw new Error(`Required context file(s) do not exist: ${missing.join(", ")}`);
  return ordered;
}
