"""behaviour: share of output lines that exactly match the hidden expected file."""

import shlex
from pathlib import Path

from rewardkit import Worker, WorkerError, criterion

HIDDEN_INPUTS = Path("/tests/data/hidden_inputs.txt")
HIDDEN_EXPECTED = Path("/tests/data/hidden_expected.txt")
WORKER_ENV = {
    "PATH": "/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin",
    "GOTOOLCHAIN": "local",
    "CGO_ENABLED": "0",
}


def split_lines(text: str) -> list[str]:
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return parts


def line_score(actual: list[str], expected: list[str]) -> float:
    total = max(len(actual), len(expected))
    if total == 0:
        return 0.0
    matches = sum(1 for got, want in zip(actual, expected) if got == want)
    return matches / total


@criterion
def behaviour(workspace: Path) -> float:
    expected = split_lines(HIDDEN_EXPECTED.read_text(encoding="utf-8"))
    script = (
        f"cd {shlex.quote(workspace.name)} && "
        'CGO_ENABLED=0 go build -o "$HOME/titlecase" . && '
        '"$HOME/titlecase"'
    )
    try:
        result = Worker(env=WORKER_ENV).run(
            script,
            files=[workspace],
            stdin=HIDDEN_INPUTS.read_bytes(),
            timeout_sec=120,
        )
    except WorkerError:
        return 0.0
    if result.returncode != 0:
        return 0.0
    actual = split_lines(result.stdout.decode("utf-8", errors="replace"))
    return line_score(actual, expected)
