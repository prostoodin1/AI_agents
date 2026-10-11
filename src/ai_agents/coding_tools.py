from __future__ import annotations

import shutil
from pathlib import Path

from .common import directory_root, iter_paths, run_process


PROJECT_MARKERS = {
    "pyproject.toml": "python", "requirements.txt": "python", "package.json": "node",
    "Cargo.toml": "rust", "go.mod": "go", "*.sln": "dotnet", "*.csproj": "dotnet",
}


def detect_project(root: str) -> dict[str, object]:
    """Detect common project types and test folders without executing project code."""
    project = directory_root(root)
    found: list[dict[str, str]] = []
    for pattern, kind in PROJECT_MARKERS.items():
        for path in project.glob(pattern):
            found.append({"type": kind, "marker": path.name})
    test_paths = []
    for path in iter_paths(project):
        relative = str(path.relative_to(project))
        if path.is_file() and (path.name.startswith("test_") or path.name.endswith((".test.js", ".test.ts", ".spec.js", ".spec.ts"))):
            test_paths.append(relative)
            if len(test_paths) >= 100:
                break
    return {"root": str(project), "project_markers": found, "test_files": test_paths, "test_file_count": len(test_paths)}


def run_checks(root: str, check: str = "tests", timeout_seconds: int = 120) -> dict[str, object]:
    """Run a known test or syntax-check command selected from project marker files; arbitrary commands are not accepted."""
    project = directory_root(root)
    allowed = {"tests", "syntax"}
    if check not in allowed:
        raise ValueError(f"check must be one of: {', '.join(sorted(allowed))}")
    if (project / "pyproject.toml").exists() or (project / "requirements.txt").exists():
        python = shutil.which("python") or shutil.which("python3")
        if not python:
            raise RuntimeError("Python was not found on PATH")
        command = [python, "-m", "pytest", "-q"] if check == "tests" else [python, "-m", "compileall", "-q", "."]
    elif (project / "package.json").exists():
        npm = shutil.which("npm")
        if not npm:
            raise RuntimeError("npm was not found on PATH")
        command = [npm, "test", "--", "--runInBand"] if check == "tests" else [npm, "run", "lint", "--if-present"]
    elif (project / "Cargo.toml").exists():
        cargo = shutil.which("cargo")
        if not cargo:
            raise RuntimeError("cargo was not found on PATH")
        command = [cargo, "test"] if check == "tests" else [cargo, "check"]
    elif (project / "go.mod").exists():
        go = shutil.which("go")
        if not go:
            raise RuntimeError("go was not found on PATH")
        command = [go, "test", "./..."] if check == "tests" else [go, "vet", "./..."]
    else:
        raise ValueError("No supported project marker was found")
    result = run_process(command, project, timeout_seconds)
    result["root"] = str(project)
    result["check"] = check
    return result
