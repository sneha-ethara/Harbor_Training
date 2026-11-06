"""Build check: go build ./... in the repository."""

import subprocess
from pathlib import Path

from rewardkit import criterion


@criterion
def build(workspace: Path) -> bool:
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=workspace,
        capture_output=True,
        timeout=180,
    )
    return result.returncode == 0
