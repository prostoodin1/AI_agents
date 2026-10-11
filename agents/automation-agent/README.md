# Prosto Automation Agent 0.1.0

Independent MCP server for explicitly declared local automation tasks.

Tools: `list_tasks`, `run_task`.

Example `.prosto-automations.json`:

```json
{
  "tasks": {
    "verify": {
      "description": "Run the test suite",
      "command": ["python", "-m", "pytest", "-q"],
      "cwd": "."
    }
  }
}
```

Commands must be argument arrays. Shell command strings are rejected.

Install and run from the extracted release folder:

```powershell
python -m pip install -r requirements.txt
python server.py
```
