from pathlib import Path
import subprocess

from rewardkit import criterion


@criterion(description="No .py files remain and `go build ./...` succeeds")
def no_python(workspace: Path) -> bool:
    if any(path.is_file() and path.suffix == ".py" for path in workspace.rglob("*")):
        return False
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
        check=False,
    )
    return result.returncode == 0
