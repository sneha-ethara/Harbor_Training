"""Check 2 — no_python (weight 1): no .py files under /workspace/repo AND the build passes.

Tied to the build on purpose: otherwise a do-nothing agent that only deletes
files would get free points.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import find_py_files, go_build_all  # noqa: E402

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402


@criterion(description="no .py files left under /workspace/repo, and the build passes")
def no_python_files(workspace: Path) -> bool:
    if find_py_files(workspace):
        return False
    return go_build_all(workspace)


rk.no_python_files()
