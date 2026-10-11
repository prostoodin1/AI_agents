from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_agents.local_tools import find_files, git_status, inspect_path, search_text


def test_find_files_is_bounded_and_skips_hidden(tmp_path: Path) -> None:
    (tmp_path / "project_notes.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "project_data.json").write_text("{}", encoding="utf-8")
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "project_secret.txt").write_text("hidden", encoding="utf-8")

    result = find_files("project", str(tmp_path), max_results=1)

    assert result["result_count"] == 1
    assert result["truncated"] is True
    assert ".hidden" not in str(result["results"])


def test_find_files_rejects_empty_query(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        find_files("  ", str(tmp_path))


def test_search_text_returns_line_and_preview(tmp_path: Path) -> None:
    (tmp_path / "alpha.py").write_text("first\nNeedle value\nthird\n", encoding="utf-8")
    (tmp_path / "ignored.bin").write_bytes(b"needle\x00binary")

    result = search_text("needle", str(tmp_path), file_glob="*")

    assert result["match_count"] == 1
    assert result["matches"][0]["line"] == 2
    assert result["matches"][0]["preview"] == "Needle value"
    assert result["skipped_files"] == 1


def test_search_text_honors_glob(tmp_path: Path) -> None:
    (tmp_path / "alpha.py").write_text("needle", encoding="utf-8")
    (tmp_path / "alpha.txt").write_text("needle", encoding="utf-8")

    result = search_text("needle", str(tmp_path), file_glob="*.py")

    assert [item["relative_path"] for item in result["matches"]] == ["alpha.py"]


def test_inspect_path_does_not_return_file_contents(tmp_path: Path) -> None:
    target = tmp_path / "secret.txt"
    target.write_text("do-not-return-this", encoding="utf-8")

    result = inspect_path(str(target))

    assert result["type"] == "file"
    assert result["size"] == len("do-not-return-this")
    assert "do-not-return-this" not in str(result)


def test_git_status_reports_changes(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "new.txt").write_text("new", encoding="utf-8")

    result = git_status(str(tmp_path))

    assert result["branch"].startswith("## ")
    assert "main" in result["branch"]
    assert any("new.txt" in line for line in result["changes"])


def test_git_status_rejects_non_repo(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Not a Git working tree"):
        git_status(str(tmp_path))
