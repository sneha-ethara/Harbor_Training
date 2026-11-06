"""Score the fraction of hidden titles the program title-cases exactly."""

import subprocess
import tempfile
from pathlib import Path

from rewardkit import criterion

HIDDEN_INPUTS = "hidden_inputs.txt"
HIDDEN_EXPECTED = "hidden_expected.txt"
DATA_DIR = Path("/tests/data")


def _load_hidden() -> tuple[bytes, str] | None:
    """Read the hidden fixtures, then remove the answer file from disk.

    The expected text stays in this process. A failed read or delete returns
    None so the submitted program is never started while the answer file remains.
    """
    expected_path = DATA_DIR / HIDDEN_EXPECTED
    try:
        inputs = (DATA_DIR / HIDDEN_INPUTS).read_bytes()
        reference = expected_path.read_text(encoding="utf-8")
        expected_path.unlink()
    except (OSError, UnicodeError):
        return None
    return inputs, reference


def _main_dir(workspace: Path) -> Path | None:
    try:
        listed = subprocess.run(
            ["go", "list", "-f", "{{if eq .Name \"main\"}}{{.Dir}}{{end}}", "./..."],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if listed.returncode != 0:
        return None
    dirs = [line for line in listed.stdout.splitlines() if line]
    if len(dirs) != 1:
        return None
    return Path(dirs[0])


def _line_fraction(expected: str, actual: str) -> float:
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    total = max(len(expected_lines), len(actual_lines))
    if total == 0:
        return 1.0
    matched = sum(
        1
        for index in range(min(len(expected_lines), len(actual_lines)))
        if expected_lines[index] == actual_lines[index]
    )
    return matched / total


@criterion(description="fraction of hidden titles that match exactly")
def behaviour(workspace: Path) -> float:
    loaded = _load_hidden()
    if loaded is None:
        return 0.0
    inputs, reference = loaded

    main_dir = _main_dir(workspace)
    if main_dir is None:
        return 0.0

    with tempfile.TemporaryDirectory() as temp_dir:
        binary = Path(temp_dir) / "titlecase"
        try:
            built = subprocess.run(
                ["go", "build", "-o", str(binary), "."],
                cwd=main_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return 0.0
        if built.returncode != 0 or not binary.is_file():
            return 0.0
        try:
            completed = subprocess.run(
                [str(binary)],
                cwd=temp_dir,
                input=inputs,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return 0.0

    if completed.returncode != 0:
        return 0.0
    try:
        actual = completed.stdout.decode("utf-8")
    except UnicodeError:
        return 0.0
    return _line_fraction(reference, actual)
