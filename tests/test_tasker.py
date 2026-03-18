import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


# Ensure the repository root is on sys.path so `import main` works when tests are run
# via `python -m unittest discover`.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import main as tasker_main
import storage


class TestTasker(unittest.TestCase):
    def test_load_tasks_missing_file_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = os.path.join(tmpdir, "tasks.json")
            tasks = storage.load_tasks(missing_path)
            self.assertEqual(tasks, {})

    def test_save_and_reload_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_path = os.path.join(tmpdir, "tasks.json")
            tasks_in = {"build": "npm run build", "dev": "npm run dev"}
            storage.save_tasks(tasks_in, tasks_path)
            tasks_out = storage.load_tasks(tasks_path)
            self.assertEqual(tasks_out, tasks_in)

    def test_add_task_persists_to_tasks_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "add", "dev", "npm run dev"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        # Success path should not exit.
                        tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(buf_err.getvalue(), "")
                self.assertIn("Added task 'dev'.", buf_out.getvalue())

                tasks = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
                self.assertEqual(tasks, {"dev": "npm run dev"})
            finally:
                os.chdir(old_cwd)

    def test_add_existing_task_errors_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("tasks.json").write_text(
                    json.dumps({"dev": "npm run dev"}, indent=2),
                    encoding="utf-8",
                )

                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "add", "dev", "npm run dev2"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        with self.assertRaises(SystemExit) as ctx:
                            tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(ctx.exception.code, 1)
                self.assertEqual(buf_out.getvalue(), "")
                self.assertEqual(buf_err.getvalue().strip(), "error: task 'dev' already exists")

                tasks = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
                self.assertEqual(tasks, {"dev": "npm run dev"})
            finally:
                os.chdir(old_cwd)

    def test_list_tasks_formats_sorted_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("tasks.json").write_text(
                    json.dumps({"dev": "npm run dev", "build": "npm run build"}, indent=2),
                    encoding="utf-8",
                )

                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "list"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(buf_err.getvalue(), "")
                self.assertEqual(
                    buf_out.getvalue().splitlines(),
                    ["build: npm run build", "dev: npm run dev"],
                )
            finally:
                os.chdir(old_cwd)

    def test_show_tasks_prints_name_and_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("tasks.json").write_text(
                    json.dumps({"build": "npm run build"}, indent=2),
                    encoding="utf-8",
                )

                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "show", "build"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(buf_err.getvalue(), "")
                self.assertEqual(buf_out.getvalue().strip(), "build: npm run build")
            finally:
                os.chdir(old_cwd)

    def test_show_unknown_task_errors_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("tasks.json").write_text(
                    json.dumps({"build": "npm run build"}, indent=2),
                    encoding="utf-8",
                )

                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "show", "missing"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        with self.assertRaises(SystemExit) as ctx:
                            tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(ctx.exception.code, 1)
                self.assertEqual(buf_out.getvalue(), "")
                self.assertEqual(buf_err.getvalue().strip(), "error: unknown task 'missing'")
            finally:
                os.chdir(old_cwd)

    def test_remove_deletes_existing_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                Path("tasks.json").write_text(
                    json.dumps({"build": "npm run build"}, indent=2),
                    encoding="utf-8",
                )

                buf_out = io.StringIO()
                buf_err = io.StringIO()

                old_argv = sys.argv[:]
                try:
                    sys.argv = ["main.py", "remove", "build"]
                    with redirect_stdout(buf_out), redirect_stderr(buf_err):
                        tasker_main.main()
                finally:
                    sys.argv = old_argv

                self.assertEqual(buf_err.getvalue(), "")
                self.assertEqual(buf_out.getvalue().strip(), "Removed task 'build'.")

                tasks = json.loads(Path("tasks.json").read_text(encoding="utf-8"))
                self.assertEqual(tasks, {})
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()

