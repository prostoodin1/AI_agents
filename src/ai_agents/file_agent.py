from mcp.server import MCPServer

from .file_tools import find_files, inspect_path, search_text

mcp = MCPServer("Prosto File Agent", version="0.1.0", instructions="Read-only local file discovery. Use only roots and paths explicitly selected by the user.")
mcp.tool()(find_files)
mcp.tool()(search_text)
mcp.tool()(inspect_path)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
