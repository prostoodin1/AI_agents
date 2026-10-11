from mcp.server import MCPServer

from .coding_tools import detect_project, run_checks

mcp = MCPServer("Prosto Coding Agent", version="0.1.0", instructions="Project inspection and allowlisted checks. Running tests executes code from the selected project.")
mcp.tool()(detect_project)
mcp.tool()(run_checks)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
