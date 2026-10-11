from pathlib import Path

import pytest
from mcp import Client

from ai_agents.file_agent import mcp
from ai_agents.file_tools import find_files, inspect_path, search_text


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_file_tools(tmp_path: Path) -> None:
    target = tmp_path / "agent_notes.txt"
    target.write_text("first\nNeedle value\n", encoding="utf-8")
    assert find_files("agent", str(tmp_path))["result_count"] == 1
    assert search_text("needle", str(tmp_path))["matches"][0]["line"] == 2
    metadata = inspect_path(str(target))
    assert metadata["type"] == "file"
    assert "Needle value" not in str(metadata)


@pytest.mark.anyio
async def test_file_agent_mcp(tmp_path: Path) -> None:
    (tmp_path / "match.txt").write_text("ok", encoding="utf-8")
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.call_tool("find_files", {"query": "match", "root": str(tmp_path)})
    assert result.structured_content["result_count"] == 1
