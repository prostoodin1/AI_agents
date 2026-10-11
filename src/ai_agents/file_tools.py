from __future__ import annotations

import fnmatch
from datetime import datetime, timezone
from pathlib import Path

from .common import bounded_limit, directory_root, iter_paths


MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
MAX_LINE_LENGTH = 500


def find_files(query: str, root: str, max_results: int = 50, include_hidden: bool = False) -> dict[str, object]:
    """Find file and folder names below an explicit root without following symlinks."""
    search_root = directory_root(root)
    needle = query.strip().casefold()
    if not needle:
        raise ValueError("Query must not be empty")
    limit = bounded_limit(max_results)
    results: list[dict[str, object]] = []
    scanned = 0
    for path in iter_paths(search_root, include_hidden):
        scanned += 1
        if needle not in path.name.casefold():
            continue
        try:
            is_dir = path.is_dir()
            results.append({
                "path": str(path), "relative_path": str(path.relative_to(search_root)),
                "type": "directory" if is_dir else "file", "size": None if is_dir else path.stat().st_size,
            })
        except OSError:
            continue
        if len(results) >= limit:
            break
    return {"root": str(search_root), "query": query, "results": results, "result_count": len(results), "scanned_paths": scanned, "truncated": len(results) >= limit}


def _looks_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(4096)
    except OSError:
        return True


def search_text(text: str, root: str, file_glob: str = "*", max_results: int = 50, case_sensitive: bool = False) -> dict[str, object]:
    """Search for literal text in reasonably sized text files."""
    search_root = directory_root(root)
    if not text:
        raise ValueError("Search text must not be empty")
    needle = text if case_sensitive else text.casefold()
    matches: list[dict[str, object]] = []
    limit = bounded_limit(max_results)
    scanned_files = 0
    for path in iter_paths(search_root):
        try:
            if not path.is_file() or path.is_symlink() or not fnmatch.fnmatch(path.name, file_glob) or path.stat().st_size > MAX_TEXT_FILE_BYTES or _looks_binary(path):
                continue
        except OSError:
            continue
        scanned_files += 1
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, 1):
                    if needle in (line if case_sensitive else line.casefold()):
                        matches.append({"path": str(path), "relative_path": str(path.relative_to(search_root)), "line": line_number, "preview": line.strip()[:MAX_LINE_LENGTH]})
                        if len(matches) >= limit:
                            break
        except OSError:
            continue
        if len(matches) >= limit:
            break
    return {"root": str(search_root), "text": text, "matches": matches, "match_count": len(matches), "scanned_files": scanned_files, "truncated": len(matches) >= limit}


def inspect_path(path: str, max_children: int = 30) -> dict[str, object]:
    """Return metadata and a bounded directory preview without file contents."""
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise ValueError(f"Path does not exist: {target}")
    stat = target.stat()
    result: dict[str, object] = {"path": str(target), "name": target.name, "type": "directory" if target.is_dir() else "file", "size": None if target.is_dir() else stat.st_size, "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(), "is_symlink": target.is_symlink()}
    if target.is_dir():
        limit = bounded_limit(max_children)
        children = sorted(target.iterdir(), key=lambda item: item.name.casefold())
        result["children"] = [{"name": item.name, "type": "directory" if item.is_dir() else "file"} for item in children[:limit]]
        result["children_truncated"] = len(children) > limit
    else:
        result["extension"] = target.suffix.lower()
    return result
