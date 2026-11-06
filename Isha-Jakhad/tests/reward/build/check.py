"""Score 1 when `go build ./...` succeeds in the repository."""

import subprocess
from pathlib import Path

from rewardkit import criterion


@criterion(description="go build ./... succeeds")
def build(workspace: Path) -> bool:
    try:
        result = subprocess.run(
            ["go", "build", "./..."],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0
