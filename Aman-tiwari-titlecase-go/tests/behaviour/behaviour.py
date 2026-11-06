"""Check 3 — behaviour (weight 4): share of HIDDEN lines that match exactly.

Builds the Go program, feeds it data/hidden_inputs.txt on stdin, and compares
each output line byte for byte with data/hidden_expected.txt.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared import DATA_DIR, build_binary, run_as_runner  # noqa: E402

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402


def _lines(data: bytes) -> list[bytes]:
    parts = data.split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return parts


@criterion(description="share of hidden titles whose output matches the original byte for byte")
def hidden_lines_match(workspace: Path) -> float:
    inputs = (DATA_DIR / "hidden_inputs.txt").read_bytes()
    expected = _lines((DATA_DIR / "hidden_expected.txt").read_bytes())

    tmp = Path(tempfile.mkdtemp(prefix="tcgo-"))
    try:
        os.chmod(tmp, 0o755)
        binary = tmp / "titlecase"
        if not build_binary(workspace, binary):
            return 0.0
        out = run_as_runner(binary, inputs)
        if out is None:
            return 0.0
        actual = _lines(out)
        correct = sum(1 for i, exp in enumerate(expected)
                      if i < len(actual) and actual[i] == exp)
        return correct / len(expected)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


rk.hidden_lines_match()
