# Prosto GitHub Agent 0.1.0

Independent read-only MCP server for local Git status/history and GitHub repository metadata.

Tools: `git_status`, `recent_commits`, `github_repository`.

Set `GITHUB_TOKEN` in the host environment only when private repository access is required. The token is never accepted as a tool argument or returned.

Run: `prosto-github-agent`
