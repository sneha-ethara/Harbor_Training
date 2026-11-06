"""build: go build ./... exits 0."""

import subprocess
from pathlib import Path

from rewardkit import criterion


def go_build_ok(workspace: Path) -> bool:
    try:
        result = subprocess.run(
            ["go", "build", "./..."],
            cwd=workspace,
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


@criterion
def build(workspace: Path) -> bool:
    return go_build_ok(workspace)
