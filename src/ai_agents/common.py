from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterator, Sequence


IGNORED_DIRECTORIES = frozenset(
    {".git", ".hg", ".svn", ".venv", "__pycache__", ".pytest_cache", "node_modules", "build", "dist"}
)
MAX_RESULTS = 200
MAX_VISITED_PATHS = 200_000


def bounded_limit(value: int) -> int:
    return max(1, min(int(value), MAX_RESULTS))


def directory_root(root: str) -> Path:
    candidate = Path(root).expanduser().resolve()
    if not candidate.exists():
        raise ValueError(f"Root does not exist: {candidate}")
    if not candidate.is_dir():
        raise ValueError(f"Root is not a directory: {candidate}")
    return candidate


def safe_child(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path must stay inside the selected root") from exc
    return candidate


def iter_paths(root: Path, include_hidden: bool = False) -> Iterator[Path]:
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
            if is_directory and not is_symlink and entry.name not in IGNORED_DIRECTORIES:
                stack.append(path)


def run_process(command: Sequence[str], cwd: Path, timeout: int = 120) -> dict[str, object]:
    try:
        completed = subprocess.run(
            list(command), cwd=cwd, capture_output=True, text=True, timeout=max(1, min(timeout, 600)), check=False
        )
    except subprocess.TimeoutExpired as exc:
        return {"command": list(command), "exit_code": None, "timed_out": True, "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
    return {
        "command": list(command),
        "exit_code": completed.returncode,
        "timed_out": False,
        "stdout": completed.stdout[-20_000:],
        "stderr": completed.stderr[-20_000:],
    }
