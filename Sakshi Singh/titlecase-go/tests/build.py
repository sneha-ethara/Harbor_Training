"""Criterion: the Go module builds."""

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


@criterion(description="`go build ./...` passes in /workspace/repo")
def build(workspace: Path) -> float:
    if not (REPO / "go.mod").is_file():
        return 0.0
    try:
        BUILD_OUT.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            # Write the binaries to a scratch directory: the repository still
            # contains the (now empty) `titlecase/` package directory, and a
            # bare `go build ./...` would fail trying to create a file with
            # that same name.
            ["go", "build", "-o", str(BUILD_OUT) + "/", "./..."],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=180,
            env=_go_env(),
        )
    except Exception:
        return 0.0
    return 1.0 if proc.returncode == 0 else 0.0
