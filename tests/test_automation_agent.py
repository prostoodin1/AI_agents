import json
import sys
from pathlib import Path

import pytest
from mcp import Client

from ai_agents.automation_agent import mcp
from ai_agents.automation_tools import list_tasks, run_task


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_named_automation(tmp_path: Path) -> None:
    config = {"tasks": {"hello": {"description": "Say hello", "command": [sys.executable, "-c", "print('hello')"], "cwd": "."}}}
    (tmp_path / ".prosto-automations.json").write_text(json.dumps(config), encoding="utf-8")
    assert list_tasks(str(tmp_path))["tasks"][0]["name"] == "hello"
    result = run_task(str(tmp_path), "hello")
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "hello"


def test_automation_cannot_escape_root(tmp_path: Path) -> None:
    config = {"tasks": {"bad": {"command": [sys.executable, "-c", "print('bad')"], "cwd": ".."}}}
    (tmp_path / ".prosto-automations.json").write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="inside"):
        run_task(str(tmp_path), "bad")


@pytest.mark.anyio
async def test_automation_agent_mcp() -> None:
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.list_tools()
    assert {tool.name for tool in result.tools} == {"list_tasks", "run_task"}
