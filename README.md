# Tasker

A lightweight, local-first CLI task runner built in Python.

Tasker lets you define and execute reusable shell commands with simple, memorable CLI commands. It is designed to be fast, minimal, and reliable.

---

## Features

- Add tasks
- List tasks
- Show task details
- Run tasks
- Remove tasks
- Local JSON storage (no cloud, no config overhead)

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/CLITasker.git
cd CLITasker

Usage
List tasks
python3 main.py list
Add a task
python3 main.py add build "npm run build"
Show a task
python3 main.py show build
Run a task
python3 main.py run build
Remove a task
python3 main.py remove build
Example
python3 main.py add hello "echo hello world"
python3 main.py run hello
Output:
hello world
Storage
Tasks are stored locally in a JSON file:
tasks.json
This file is created automatically
It is intentionally ignored by Git
Each task is stored as:
{
  "build": "npm run build",
  "dev": "npm run dev"
}
Project Structure
.
├── main.py        # CLI entry point
├── storage.py     # Load/save tasks
├── runner.py      # Execute commands
├── tests/         # Unit tests
├── .gitignore
└── README.md
Running Tests
python3 -m unittest discover -s tests -v
