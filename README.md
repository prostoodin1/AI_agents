# AI_agents

Four independent, small MCP agents for OpenClaw, OpenHands, Codex, Claude Code, Cursor, VS Code, and other MCP-compatible hosts.

| Agent | Purpose | Tools | Release tag |
| --- | --- | --- | --- |
| File Agent | Safe local file discovery | `find_files`, `search_text`, `inspect_path` | `file-agent-v0.1.0` |
| GitHub Agent | Read-only Git and GitHub inspection | `git_status`, `recent_commits`, `github_repository` | `github-agent-v0.1.0` |
| Coding Agent | Detect projects and run known checks | `detect_project`, `run_checks` | `coding-agent-v0.1.0` |
| Automation Agent | Run named project automations | `list_tasks`, `run_task` | `automation-agent-v0.1.0` |

These are four separate server processes and entry points, not one large server with four modes. Shared low-level safety helpers are reused to avoid duplicated bugs.

## Install for development

Python 3.10 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Run

Install the release for the agent you want, then use its own command:

```text
prosto-file-agent
prosto-github-agent
prosto-coding-agent
prosto-automation-agent
```

Each release archive contains only that agent, its shared runtime, instructions, license, and tests.

## Safety boundaries

- File Agent is read-only and does not follow directory symlinks.
- GitHub Agent is read-only; an optional `GITHUB_TOKEN` environment variable enables private repository metadata without passing the token through MCP.
- Coding Agent accepts only known test/check profiles. Tests execute code from the selected project.
- Automation Agent accepts only argument arrays declared in `.prosto-automations.json`; it never evaluates a shell command string.

## OpenClaw + OpenHands direction

These agents are the custom tool layer. OpenClaw and OpenHands can connect to the individual MCP servers as hosts/orchestrators. No model provider or API key is bundled.

## License

MIT
