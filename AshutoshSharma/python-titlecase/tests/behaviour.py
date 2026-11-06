"""Share of output lines that exactly match the hidden expected titles."""

import shlex
from pathlib import Path

from rewardkit import Worker, WorkerError, criterion

HIDDEN_INPUTS = Path("/tests/data/hidden_inputs.txt")
HIDDEN_EXPECTED = Path("/tests/data/hidden_expected.txt")

GO_ENV = {
    "PATH": "/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin",
    "GOROOT": "/usr/local/go",
    "GOPROXY": "off",
    "GOSUMDB": "off",
    "GO111MODULE": "on",
    "CGO_ENABLED": "0",
}


def split_lines(data: bytes) -> list[bytes]:
    if data.endswith(b"\n"):
        data = data[:-1]
    if data == b"":
        return []
    return data.split(b"\n")


def line_score(actual: bytes, expected: bytes) -> float:
    got = split_lines(actual)
    want = split_lines(expected)
    total = max(len(got), len(want))
    if total == 0:
        return 1.0
    matches = sum(
        1
        for index in range(total)
        if index < len(got) and index < len(want) and got[index] == want[index]
    )
    return matches / total


@criterion
def behaviour(workspace: Path) -> float:
    if not workspace.is_dir():
        return 0.0
    script = (
        f"cd {shlex.quote(workspace.name)} && "
        'mkdir -p "$HOME/gocache" && '
        'GOCACHE="$HOME/gocache" GOTMPDIR="$HOME" '
        'go build -o "$HOME/titlecase" . && exec "$HOME/titlecase"'
    )
    try:
        result = Worker(env=GO_ENV).run(
            script,
            files=[workspace],
            stdin=HIDDEN_INPUTS.read_bytes(),
            timeout_sec=180,
        )
    except WorkerError:
        return 0.0
    if result.returncode != 0:
        return 0.0
    return line_score(result.stdout, HIDDEN_EXPECTED.read_bytes())
