"""Criterion: share of hidden lines that match python-titlecase exactly."""

import os
import subprocess
from pathlib import Path

from rewardkit import criterion

REPO = Path("/workspace/repo")
HIDDEN_INPUTS = Path("/tests/data/hidden_inputs.txt")
HIDDEN_EXPECTED = Path("/tests/data/hidden_expected.txt")
BINARY = Path("/tmp/titlecase_go")


def _go_env() -> dict:
    env = dict(os.environ)
    env["GOTOOLCHAIN"] = "local"
    env["GOCACHE"] = "/tmp/go-build"
    env["GOFLAGS"] = "-mod=mod"
    return env


@criterion(description="share of hidden titles reproduced byte-for-byte")
def behaviour(workspace: Path) -> float:
    if not (REPO / "go.mod").is_file():
        return 0.0
    try:
        build = subprocess.run(
            ["go", "build", "-o", str(BINARY), "."],
            cwd=str(REPO),
            capture_output=True,
            timeout=180,
            env=_go_env(),
        )
        if build.returncode != 0:
            return 0.0

        expected = HIDDEN_EXPECTED.read_bytes().splitlines()
        if not expected:
            return 0.0

        proc = subprocess.run(
            [str(BINARY)],
            input=HIDDEN_INPUTS.read_bytes(),
            capture_output=True,
            timeout=180,
            env=_go_env(),
        )
        if proc.returncode != 0:
            return 0.0

        got = proc.stdout.splitlines()
        correct = sum(
            1 for i, want in enumerate(expected) if i < len(got) and got[i] == want
        )
        return correct / len(expected)
    except Exception:
        return 0.0
