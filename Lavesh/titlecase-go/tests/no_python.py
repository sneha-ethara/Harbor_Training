import subprocess
from pathlib import Path

from rewardkit import criterion


@criterion
def no_python_sources(workspace: Path) -> bool:
    """Score 1 only when the repo has no .py files and go build ./... exits 0."""
    has_python = any(
        path.is_file() and path.name.endswith(".py") for path in workspace.rglob("*")
    )
    if has_python:
        print("python_files=present")
        return False

    try:
        result = subprocess.run(
            ["go", "build", "./..."],
            cwd=workspace,
            capture_output=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        print("build_timeout=1")
        return False

    print(f"build_exit={result.returncode}")
    return result.returncode == 0
