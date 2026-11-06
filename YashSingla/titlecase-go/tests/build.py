from pathlib import Path
import subprocess
import tempfile

from rewardkit import criterion


@criterion(description="`go build ./...` succeeds in the submitted repository")
def build(workspace: Path) -> bool:
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
        check=False,
    )
    return result.returncode == 0
