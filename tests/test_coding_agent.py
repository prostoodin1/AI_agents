from pathlib import Path

import pytest
from mcp import Client

from ai_agents.coding_agent import mcp
from ai_agents.coding_tools import detect_project, run_checks


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_detect_and_compile(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='sample'\nversion='0'\n", encoding="utf-8")
    (tmp_path / "sample.py").write_text("value = 1\n", encoding="utf-8")
    assert detect_project(str(tmp_path))["project_markers"][0]["type"] == "python"
    assert run_checks(str(tmp_path), "syntax")["exit_code"] == 0


@pytest.mark.anyio
async def test_coding_agent_mcp() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.list_tools()
    assert {tool.name for tool in result.tools} == {"detect_project", "run_checks"}
