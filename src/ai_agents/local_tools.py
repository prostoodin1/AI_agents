from __future__ import annotations

import fnmatch
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


DEFAULT_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "build",
        "dist",
    }
)
MAX_RESULTS_LIMIT = 200
MAX_VISITED_PATHS = 200_000
MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
MAX_LINE_LENGTH = 500


def _bounded_limit(value: int) -> int:
    return max(1, min(int(value), MAX_RESULTS_LIMIT))


def _directory_root(root: str) -> Path:
    candidate = Path(root).expanduser().resolve()
    if not candidate.exists():
        raise ValueError(f"Root does not exist: {candidate}")
    if not candidate.is_dir():
        raise ValueError(f"Root is not a directory: {candidate}")
    return candidate


def _iter_paths(root: Path, include_hidden: bool) -> Iterator[Path]:
    stack = [root]
    visited = 0
    while stack and visited < MAX_VISITED_PATHS:
        directory = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold())
        except (OSError, PermissionError):
            continue
        for entry in entries:
            visited += 1
            if visited > MAX_VISITED_PATHS:
                return
            if not include_hidden and entry.name.startswith("."):
                continue
            path = Path(entry.path)
            yield path
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
                is_symlink = entry.is_symlink()
            except OSError:
                continue
            if is_directory and not is_symlink and entry.name not in DEFAULT_IGNORED_DIRECTORIES:
                stack.append(path)


def find_files(query: str, root: str, max_results: int = 50, include_hidden: bool = False) -> dict[str, object]:
    """Find file and folder names below an explicit root without following symlinks."""

    search_root = _directory_root(root)
    needle = query.strip().casefold()
    if not needle:
        raise ValueError("Query must not be empty")
    limit = _bounded_limit(max_results)
    results: list[dict[str, object]] = []
    scanned = 0
    truncated = False
    for path in _iter_paths(search_root, include_hidden):
        scanned += 1
        if needle not in path.name.casefold():
            continue
        try:
            relative = path.relative_to(search_root)
            is_dir = path.is_dir()
            size = None if is_dir else path.stat().st_size
        except OSError:
            continue
        results.append(
            {
                "path": str(path),
                "relative_path": str(relative),
                "type": "directory" if is_dir else "file",
                "size": size,
            }
        )
        if len(results) >= limit:
            truncated = True
            break
    return {
        "root": str(search_root),
        "query": query,
        "results": results,
        "result_count": len(results),
        "scanned_paths": scanned,
        "truncated": truncated,
    }


def _looks_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(4096)
    except OSError:
        return True


def search_text(
    text: str,
    root: str,
    file_glob: str = "*",
    max_results: int = 50,
    case_sensitive: bool = False,
    include_hidden: bool = False,
) -> dict[str, object]:
    """Search for literal text in small text files below an explicit root."""

    search_root = _directory_root(root)
    if not text:
        raise ValueError("Search text must not be empty")
    limit = _bounded_limit(max_results)
    needle = text if case_sensitive else text.casefold()
    matches: list[dict[str, object]] = []
    scanned_files = 0
    skipped_files = 0
    truncated = False
    for path in _iter_paths(search_root, include_hidden):
        try:
            if not path.is_file() or path.is_symlink() or not fnmatch.fnmatch(path.name, file_glob):
                continue
            if path.stat().st_size > MAX_TEXT_FILE_BYTES or _looks_binary(path):
                skipped_files += 1
                continue
        except OSError:
            continue
        scanned_files += 1
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, start=1):
                    haystack = line if case_sensitive else line.casefold()
                    if needle not in haystack:
                        continue
                    matches.append(
                        {
                            "path": str(path),
                            "relative_path": str(path.relative_to(search_root)),
                            "line": line_number,
                            "preview": line.strip()[:MAX_LINE_LENGTH],
                        }
                    )
                    if len(matches) >= limit:
                        truncated = True
                        break
        except (OSError, UnicodeError):
            skipped_files += 1
        if truncated:
            break
    return {
        "root": str(search_root),
        "text": text,
        "file_glob": file_glob,
        "matches": matches,
        "match_count": len(matches),
        "scanned_files": scanned_files,
        "skipped_files": skipped_files,
        "truncated": truncated,
    }


def inspect_path(path: str, max_children: int = 30) -> dict[str, object]:
    """Return metadata for one path and a bounded child-name preview for directories."""

    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise ValueError(f"Path does not exist: {target}")
    stat = target.stat()
    result: dict[str, object] = {
        "path": str(target),
        "name": target.name,
        "type": "directory" if target.is_dir() else "file",
        "size": None if target.is_dir() else stat.st_size,
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "is_symlink": target.is_symlink(),
    }
    if target.is_file():
        result["extension"] = target.suffix.lower()
        return result
    limit = _bounded_limit(max_children)
    try:
        children = sorted(target.iterdir(), key=lambda item: item.name.casefold())
    except (OSError, PermissionError):
        result["children"] = []
        result["children_error"] = "Directory could not be listed"
        return result
    result["children"] = [
        {"name": item.name, "type": "directory" if item.is_dir() else "file"}
        for item in children[:limit]
    ]
    result["children_truncated"] = len(children) > limit
    return result


def git_status(repo_path: str) -> dict[str, object]:
    """Return compact, read-only Git status for an existing working tree."""

    root = _directory_root(repo_path)
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git was not found on PATH")
    probe = subprocess.run(
        [git, "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if probe.returncode != 0:
        raise ValueError(f"Not a Git working tree: {root}")
    top_level = Path(probe.stdout.strip()).resolve()
    status = subprocess.run(
        [git, "-C", str(top_level), "status", "--short", "--branch"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip() or "git status failed")
    lines = status.stdout.splitlines()
    return {
        "repository": str(top_level),
        "branch": lines[0] if lines else "",
        "changes": lines[1:201],
        "change_count": max(0, len(lines) - 1),
        "truncated": len(lines) > 201,
    }
