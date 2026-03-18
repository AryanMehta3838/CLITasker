#!/usr/bin/env python3
"""Task execution: run a command string in the shell."""

import subprocess


def run_task(command: str) -> int:
    """Execute the command in the shell.

    Streams stdout/stderr to the terminal.
    Returns the subprocess exit code.
    """
    if not command or not command.strip():
        raise ValueError("command must be non-empty")

    result = subprocess.run(command, shell=True)
    return result.returncode
