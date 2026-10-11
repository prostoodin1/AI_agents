from __future__ import annotations

import json
import os
import re
import shutil
import urllib.error
import urllib.request

from .common import directory_root, run_process


def _git(root: str, *args: str) -> dict[str, object]:
    repo = directory_root(root)
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git was not found on PATH")
    probe = run_process([git, "rev-parse", "--show-toplevel"], repo, 15)
    if probe["exit_code"] != 0:
        raise ValueError(f"Not a Git working tree: {repo}")
    return run_process([git, *args], repo, 30)


def git_status(repo_path: str) -> dict[str, object]:
    """Return branch and compact local changes for a Git repository."""
    result = _git(repo_path, "status", "--short", "--branch")
    lines = str(result["stdout"]).splitlines()
    return {"branch": lines[0] if lines else "", "changes": lines[1:201], "change_count": max(0, len(lines) - 1), "truncated": len(lines) > 201}


def recent_commits(repo_path: str, count: int = 10) -> dict[str, object]:
    """Return recent local commit identifiers, dates, and subjects."""
    count = max(1, min(int(count), 50))
    result = _git(repo_path, "log", f"-{count}", "--date=iso-strict", "--pretty=format:%h%x09%ad%x09%s")
    if result["exit_code"] != 0:
        raise RuntimeError(str(result["stderr"]) or "git log failed")
    commits = []
    for line in str(result["stdout"]).splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            commits.append({"id": parts[0], "date": parts[1], "subject": parts[2]})
    return {"commits": commits, "count": len(commits)}


def github_repository(repository: str) -> dict[str, object]:
    """Read GitHub repository metadata. GITHUB_TOKEN is used from the environment when available."""
    match = re.fullmatch(r"(?:https://github\.com/)?([^/]+)/([^/]+?)(?:\.git)?/?", repository.strip())
    if not match:
        raise ValueError("Repository must be owner/name or a github.com URL")
    owner, name = match.groups()
    request = urllib.request.Request(f"https://api.github.com/repos/{owner}/{name}", headers={"Accept": "application/vnd.github+json", "User-Agent": "prosto-github-agent/0.1.0"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}") from exc
    return {key: data.get(key) for key in ("full_name", "private", "description", "default_branch", "archived", "html_url", "open_issues_count", "updated_at")}
