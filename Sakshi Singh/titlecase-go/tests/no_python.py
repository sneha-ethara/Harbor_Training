"""Criterion: the Go module builds and no Python file was left behind."""

import os
import subprocess
from pathlib import Path

from rewardkit import criterion

REPO = Path("/workspace/repo")
BUILD_OUT = Path("/tmp/go-build-out")


def _go_env() -> dict:
    env = dict(os.environ)
    env["GOTOOLCHAIN"] = "local"
    env["GOCACHE"] = "/tmp/go-build"
    env["GOFLAGS"] = "-mod=mod"
    return env


@criterion(description="no .py file remains under /workspace/repo and the build passes")
def no_python(workspace: Path) -> float:
    if not (REPO / "go.mod").is_file():
        return 0.0
    try:
        BUILD_OUT.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            ["go", "build", "-o", str(BUILD_OUT) + "/", "./..."],
            cwd=str(REPO),
            capture_output=True,
            timeout=180,
            env=_go_env(),
        )
    except Exception:
        return 0.0
    if proc.returncode != 0:
        return 0.0

    leftovers = [p for p in REPO.rglob("*.py") if p.is_file()]
    return 1.0 if not leftovers else 0.0
