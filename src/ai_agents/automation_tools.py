from __future__ import annotations

import json
from pathlib import Path

from .common import directory_root, run_process, safe_child


CONFIG_NAME = ".prosto-automations.json"


def _tasks(root: Path) -> dict[str, object]:
    config = root / CONFIG_NAME
    if not config.exists():
        return {}
    data = json.loads(config.read_text(encoding="utf-8"))
    tasks = data.get("tasks", {})
    if not isinstance(tasks, dict):
        raise ValueError("tasks must be a JSON object")
    return tasks


def list_tasks(root: str) -> dict[str, object]:
    """List named automation tasks from .prosto-automations.json without executing them."""
    project = directory_root(root)
    tasks = _tasks(project)
    result = []
    for name, spec in sorted(tasks.items()):
        if isinstance(spec, dict):
            result.append({"name": name, "description": str(spec.get("description", "")), "working_directory": str(spec.get("cwd", "."))})
    return {"root": str(project), "config": str(project / CONFIG_NAME), "tasks": result, "task_count": len(result)}


def run_task(root: str, task_name: str, timeout_seconds: int = 120) -> dict[str, object]:
    """Run one explicitly named, argument-array task from .prosto-automations.json without a shell."""
    project = directory_root(root)
    spec = _tasks(project).get(task_name)
    if not isinstance(spec, dict):
        raise ValueError(f"Unknown automation task: {task_name}")
    command = spec.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        raise ValueError("Task command must be a non-empty array of strings")
    cwd = safe_child(project, str(spec.get("cwd", ".")))
    if not cwd.is_dir():
        raise ValueError("Task working directory does not exist")
    result = run_process(command, cwd, timeout_seconds)
    result.update({"root": str(project), "task": task_name, "working_directory": str(cwd)})
    return result
