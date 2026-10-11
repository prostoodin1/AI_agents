from __future__ import annotations

from pathlib import Path

import pytest
from mcp import Client

from server import mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_mcp_find_files_tool(tmp_path: Path) -> None:
    (tmp_path / "agent_notes.md").write_text("ready", encoding="utf-8")
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.call_tool(
            "find_files",
            {"query": "agent", "root": str(tmp_path), "max_results": 10},
        )

    assert result.is_error is False
    assert result.structured_content["result_count"] == 1
    assert result.structured_content["results"][0]["relative_path"] == "agent_notes.md"
