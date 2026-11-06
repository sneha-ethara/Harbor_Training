"""Score 1 only when the repository has no Python files and still builds."""

import subprocess
from pathlib import Path

from rewardkit import criterion


@criterion(description="no .py files remain and go build ./... succeeds")
def no_python(workspace: Path) -> bool:
    if any(workspace.rglob("*.py")):
        return False
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
