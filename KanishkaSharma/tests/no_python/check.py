"""No Python sources may remain, and the Go build must still pass."""

import subprocess
from pathlib import Path

from rewardkit import criterion


def _build_passes(workspace: Path) -> bool:
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=workspace,
        capture_output=True,
        timeout=180,
    )
    return result.returncode == 0


@criterion
def no_python(workspace: Path) -> bool:
    if any(path.is_file() for path in workspace.rglob("*.py")):
        return False
    return _build_passes(workspace)
