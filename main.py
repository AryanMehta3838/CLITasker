#!/usr/bin/env python3
"""Minimal CLI app 'tasker' with list, add, run (list uses JSON storage)."""

import argparse
import sys

from runner import run_task
from storage import TaskStorageError, load_tasks, save_tasks


class TaskerArgumentParser(argparse.ArgumentParser):
    """Argparse parser with short, actionable error messages."""

    def error(self, message: str) -> None:  # type: ignore[override]
        # Keep argparse errors compact and actionable; avoid full stack traces.
        print(f"error: {message}", file=sys.stderr)
        self.exit(2)


def main() -> None:
    parser = TaskerArgumentParser(prog="tasker")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    subparsers.add_parser("list", help="List all saved tasks")

    add_parser = subparsers.add_parser("add", help="Add a task (name -> command)")
    add_parser.add_argument("name", help="Task name")
    add_parser.add_argument("command", help="Shell command to store")

    run_parser = subparsers.add_parser("run", help="Run a task by name")
    run_parser.add_argument("name", help="Task name")

    show_parser = subparsers.add_parser("show", help="Show the command for a task")
    show_parser.add_argument("name", help="Task name")

    remove_parser = subparsers.add_parser("remove", help="Remove a task by name")
    remove_parser.add_argument("name", help="Task name")

    args = parser.parse_args()

    if args.subcommand == "list":
        try:
            tasks = load_tasks()
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        for name in sorted(tasks):
            print(f"{name}: {tasks[name]}")
    elif args.subcommand == "add":
        name = args.name.strip()
        command = args.command.strip()

        if not name:
            print("error: task name must be non-empty", file=sys.stderr)
            sys.exit(1)
        if not command:
            print("error: command must be non-empty", file=sys.stderr)
            sys.exit(1)

        try:
            tasks = load_tasks()
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        if name in tasks:
            print(f"error: task '{name}' already exists", file=sys.stderr)
            sys.exit(1)

        tasks[name] = command

        try:
            save_tasks(tasks)
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Added task '{name}'.")
    elif args.subcommand == "run":
        name = args.name.strip()
        if not name:
            print("error: task name must be non-empty", file=sys.stderr)
            sys.exit(1)

        try:
            tasks = load_tasks()
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        if name not in tasks:
            print(f"error: unknown task '{name}'", file=sys.stderr)
            sys.exit(1)

        command = tasks[name]
        if not command or not command.strip():
            print(f"error: task '{name}' has an empty command", file=sys.stderr)
            sys.exit(1)

        try:
            exit_code = run_task(command)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        sys.exit(exit_code)
    elif args.subcommand == "show":
        name = args.name.strip()
        if not name:
            print("error: task name must be non-empty", file=sys.stderr)
            sys.exit(1)

        try:
            tasks = load_tasks()
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        if name not in tasks:
            print(f"error: unknown task '{name}'", file=sys.stderr)
            sys.exit(1)

        print(f"{name}: {tasks[name]}")
    elif args.subcommand == "remove":
        name = args.name.strip()
        if not name:
            print("error: task name must be non-empty", file=sys.stderr)
            sys.exit(1)

        try:
            tasks = load_tasks()
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        if name not in tasks:
            print(f"error: unknown task '{name}'", file=sys.stderr)
            sys.exit(1)

        del tasks[name]

        try:
            save_tasks(tasks)
        except TaskStorageError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Removed task '{name}'.")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
