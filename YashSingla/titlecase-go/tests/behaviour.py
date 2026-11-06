from pathlib import Path
import subprocess
import tempfile

from rewardkit import criterion


@criterion(description="Share of hidden title lines matching the original Python titlecase outputs exactly")
def behaviour(workspace: Path) -> float:
    data = Path("/tests/data")
    inputs = (data / "hidden_inputs.txt").read_bytes()
    expected = (data / "hidden_expected.txt").read_bytes().splitlines()
    if not expected:
        return 0.0

    with tempfile.TemporaryDirectory(prefix="titlecase-go-") as temp_dir:
        executable = Path(temp_dir) / "titlecase"
        build = subprocess.run(
            ["go", "build", "-o", str(executable), "."],
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
        if build.returncode != 0:
            return 0.0
        result = subprocess.run(
            [str(executable)],
            cwd=workspace,
            input=inputs,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
        if result.returncode != 0:
            return 0.0

    actual = result.stdout.splitlines()
    compared = max(len(actual), len(expected))
    if compared == 0:
        return 0.0
    matches = sum(left == right for left, right in zip(actual, expected))
    return matches / compared
