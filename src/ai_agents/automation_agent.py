from mcp.server import MCPServer

from .automation_tools import list_tasks, run_task

mcp = MCPServer("Prosto Automation Agent", version="0.1.0", instructions="Runs only named command arrays declared in the selected project's .prosto-automations.json. No shell strings are accepted.")
mcp.tool()(list_tasks)
mcp.tool()(run_task)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
