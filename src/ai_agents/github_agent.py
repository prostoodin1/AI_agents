from mcp.server import MCPServer

from .github_tools import git_status, github_repository, recent_commits

mcp = MCPServer("Prosto GitHub Agent", version="0.1.0", instructions="Read-only Git and GitHub inspection. Never asks for or returns access tokens.")
mcp.tool()(git_status)
mcp.tool()(recent_commits)
mcp.tool()(github_repository)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
