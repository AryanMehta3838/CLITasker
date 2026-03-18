#!/usr/bin/env python3
"""JSON-backed task storage."""

import json
import os


class TaskStorageError(Exception):
    """Raised when tasks cannot be loaded or saved."""


def load_tasks(path: str = "tasks.json") -> dict[str, str]:
    """Load tasks from a JSON file.

    If the file is missing, returns an empty dict.
    If the file exists but is invalid/corrupt, raises TaskStorageError.
    """
    if not os.path.isfile(path):
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise TaskStorageError("tasks.json contains invalid JSON") from e
    except OSError as e:
        raise TaskStorageError(f"cannot read {path}") from e

    if not isinstance(data, dict):
        raise TaskStorageError("tasks.json must be a JSON object")

    return {k: str(v) for k, v in data.items()}


def save_tasks(tasks: dict[str, str], path: str = "tasks.json") -> None:
    """Write tasks to a JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        raise TaskStorageError(f"cannot write {path}") from e
