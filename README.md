# AI_agents

Small, testable tools that AI hosts can use without sending your files to a new AI provider.

The first release is **Local Workspace Tools**, a read-only MCP server for Codex, OpenHands, OpenClaw, Claude Code, Cursor, VS Code, and other MCP-compatible hosts.

## Included tools

- `find_files` — bounded file and folder name search.
- `search_text` — bounded literal text search inside reasonably sized text files.
- `inspect_path` — metadata and a small directory preview without reading file contents.
- `git_status` — compact read-only Git status for a repository.

All roots and paths must be supplied explicitly. The server does not modify, upload, or delete files, does not scan symlink targets, and does not need an API key.

## Install

Python 3.10 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Run as an MCP server

```powershell
.\.venv\Scripts\python.exe server.py
```

The server uses MCP over stdio and normally stays silent while it waits for a host.

Example host configuration:

```json
{
  "mcpServers": {
    "prosto-local-tools": {
      "command": "C:\\absolute\\path\\AI_agents\\.venv\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\AI_agents\\server.py"]
    }
  }
}
```

Use absolute paths. Host-specific configuration locations differ, but the launch command is the same.

## Development principles

- no API keys for local tools;
- read-only by default;
- explicit and bounded filesystem scope;
- structured results that cost fewer model tokens;
- tests before publishing changes.

## License

MIT
