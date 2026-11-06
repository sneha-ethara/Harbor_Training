"""No Python files remain, and the Go build still passes."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from rewardkit import criterion


def go_build_succeeds(workspace: Path) -> bool:
    if not workspace.is_dir():
        return False
    cache = tempfile.mkdtemp(prefix="gocache-")
    output = tempfile.mkdtemp(prefix="goout-")
    env = os.environ.copy()
    env.update(
        {
            "GOCACHE": cache,
            "GOTMPDIR": cache,
            "GOPROXY": "off",
            "GOSUMDB": "off",
            "CGO_ENABLED": "0",
        }
    )
    try:
        result = subprocess.run(
            ["go", "build", "-o", output + os.sep, "./..."],
            cwd=workspace,
            capture_output=True,
            timeout=120,
            env=env,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False
    finally:
        shutil.rmtree(cache, ignore_errors=True)
        shutil.rmtree(output, ignore_errors=True)


@criterion
def no_python(workspace: Path) -> bool:
    if not workspace.is_dir():
        return False
    has_python = any(path.is_file() for path in workspace.rglob("*.py"))
    return (not has_python) and go_build_succeeds(workspace)
