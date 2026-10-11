from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


async def main() -> None:
    scripts = Path(sys.executable).parent
    suffix = ".exe" if sys.platform == "win32" else ""
    for name in ("file", "github", "coding", "automation"):
        if len(sys.argv) > 1:
            release_root = Path(sys.argv[1]).resolve()
            stage = next((release_root / f"{name}-agent").glob("Prosto-*-Agent-0.1.0"))
            command = Path(sys.executable)
            args = [str(stage / "server.py")]
        else:
            command = scripts / f"prosto-{name}-agent{suffix}"
            args = []
        async with Client(StdioServerParameters(command=str(command), args=args), raise_exceptions=True) as client:
            result = await client.list_tools()
            tools = ", ".join(tool.name for tool in result.tools)
            print(f"{name}_agent: {tools}")


if __name__ == "__main__":
    asyncio.run(main())
