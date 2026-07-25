/** Minimal GitHub Contents API client; GitHub remains the document source of truth. */
export class GitHubClient {
  constructor({ token, fetchImpl = fetch, apiUrl = "https://api.github.com" }) {
    if (!token) throw new Error("GITHUB_TOKEN is required.");
    this.token = token;
    this.fetch = fetchImpl;
    this.apiUrl = apiUrl.replace(/\/$/, "");
  }

  async request(path, options = {}) {
    const response = await this.fetch(`${this.apiUrl}${path}`, {
      ...options,
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${this.token}`,
        "X-GitHub-Api-Version": "2022-11-28",
        ...options.headers,
      },
    });
    if (response.status === 204) return null;
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = body.message || response.statusText;
      throw new Error(`GitHub request failed (${response.status}) for ${path}: ${detail}`);
    }
    return body;
  }

  repoPath(owner, repo, filePath) {
    return `/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/${filePath.split("/").map(encodeURIComponent).join("/")}`;
  }

  async assertBranch(owner, repo, branch) {
    try {
      await this.request(`/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/git/ref/heads/${encodeURIComponent(branch)}`);
    } catch (error) {
      throw new Error(`Repository or branch does not exist (${owner}/${repo}@${branch}): ${error.message}`);
    }
  }

  async getFile(owner, repo, branch, filePath) {
    const path = `${this.repoPath(owner, repo, filePath)}?ref=${encodeURIComponent(branch)}`;
    const file = await this.request(path);
    if (file.type !== "file" || typeof file.content !== "string") {
      throw new Error(`GitHub path is not a file: ${filePath}`);
    }
    return {
      path: filePath,
      sha: file.sha,
      content: Buffer.from(file.content.replace(/\n/g, ""), "base64").toString("utf8"),
    };
  }

  async fileExists(owner, repo, branch, filePath) {
    try {
      await this.getFile(owner, repo, branch, filePath);
      return true;
    } catch (error) {
      if (error.message.includes("(404)")) return false;
      throw error;
    }
  }

  async writeFile({ owner, repo, branch, path, content, message }) {
    await this.assertBranch(owner, repo, branch);
    let existing;
    try {
      existing = await this.getFile(owner, repo, branch, path);
    } catch (error) {
      if (!error.message.includes("(404)")) throw error;
    }
    const result = await this.request(this.repoPath(owner, repo, path), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        content: Buffer.from(content, "utf8").toString("base64"),
        branch,
        ...(existing ? { sha: existing.sha } : {}),
      }),
    });
    return { repository: `${owner}/${repo}`, branch, path, commit_sha: result.commit.sha };
  }
}
