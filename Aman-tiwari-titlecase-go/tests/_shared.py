"""Shared helpers for the checks (no criteria defined here)."""

import os
import pwd
import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
DATA_DIR = TESTS_DIR / "data"
RUN_USER = "runner"


def go_build_all(workspace: Path) -> bool:
    """`go build ./...` in the repo. True if it passes."""
    if not (workspace / "go.mod").is_file():
        return False
    try:
        r = subprocess.run(["go", "build", "./..."], cwd=workspace,
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False
    return r.returncode == 0


def build_binary(workspace: Path, out: Path) -> bool:
    """Build the module-root main package to `out`."""
    if not (workspace / "go.mod").is_file():
        return False
    try:
        r = subprocess.run(["go", "build", "-o", str(out), "."], cwd=workspace,
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False
    return r.returncode == 0 and out.is_file()


def run_as_runner(binary: Path, stdin: bytes, timeout: int = 120) -> bytes | None:
    """Run the agent's program as an unprivileged user (cannot read /tests)."""
    pw = pwd.getpwnam(RUN_USER)
    os.chmod(binary, 0o755)
    try:
        r = subprocess.run([str(binary)], input=stdin, capture_output=True,
                           timeout=timeout, user=pw.pw_uid, group=pw.pw_gid,
                           extra_groups=[], cwd="/tmp",
                           env={"PATH": "/usr/bin:/bin", "HOME": pw.pw_dir})
    except subprocess.TimeoutExpired:
        return None
    return r.stdout


def find_py_files(workspace: Path) -> list[str]:
    found = []
    for root, _dirs, files in os.walk(workspace, followlinks=False):
        for f in files:
            if f.lower().endswith(".py"):
                found.append(os.path.join(root, f))
    return found
