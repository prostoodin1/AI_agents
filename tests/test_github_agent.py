import subprocess
from pathlib import Path

import pytest
from mcp import Client

from ai_agents.github_agent import mcp
from ai_agents.github_tools import git_status, recent_commits


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    (path / "tracked.txt").write_text("one", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True)


def test_git_tools(tmp_path: Path) -> None:
    _repo(tmp_path)
    (tmp_path / "new.txt").write_text("new", encoding="utf-8")
    assert git_status(str(tmp_path))["change_count"] == 1
    assert recent_commits(str(tmp_path))["commits"][0]["subject"] == "initial"


@pytest.mark.anyio
async def test_github_agent_mcp(tmp_path: Path) -> None:
    _repo(tmp_path)
    async with Client(mcp, raise_exceptions=True) as client:
        result = await client.list_tools()
    assert {tool.name for tool in result.tools} == {"git_status", "recent_commits", "github_repository"}
