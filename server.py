from __future__ import annotations

from mcp.server import MCPServer

from ai_agents.local_tools import find_files, git_status, inspect_path, search_text


mcp = MCPServer(
    "Prosto Local Workspace Tools",
    version="0.1.0",
    instructions=(
        "Read-only local workspace tools. Always use an explicit root or path supplied by the user. "
        "Results are bounded and symlink targets are not scanned."
    ),
)

mcp.tool()(find_files)
mcp.tool()(search_text)
mcp.tool()(inspect_path)
mcp.tool()(git_status)


if __name__ == "__main__":
    mcp.run()
