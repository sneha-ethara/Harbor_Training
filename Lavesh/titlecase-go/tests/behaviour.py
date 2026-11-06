import shutil
import subprocess
from pathlib import Path

from rewardkit import criterion

DATA = Path(__file__).parent / "data"
TIMEOUT_SEC = 120
JAIL = Path("/tmp/titlecase-jail")


def _stage_jail(binary: Path) -> Path:
    """Copy the binary and its libraries into a directory with no answer files.

    The verifier has already stored the expected bytes in memory. The graded
    program is started with chroot as uid 65534, so its filesystem root is this
    directory and it cannot open /tests/data or any expected-answer file.
    The name "nobody" is not used: chroot resolves user names inside the jail,
    and the jail has no /etc/passwd.
    """
    if JAIL.exists():
        shutil.rmtree(JAIL)
    JAIL.mkdir(mode=0o755)
    dest = JAIL / "titlecase"
    shutil.copy2(binary, dest)
    dest.chmod(0o755)

    try:
        listed = subprocess.run(
            ["ldd", str(binary)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        listed = None
    if listed is not None and listed.returncode == 0:
        for line in listed.stdout.splitlines():
            for token in line.split():
                if not token.startswith("/"):
                    continue
                source = Path(token)
                if not source.is_file():
                    continue
                target = JAIL / source.relative_to("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(source, target)

    leaked = [path for path in JAIL.rglob("*") if "expected" in path.name]
    if leaked:
        raise RuntimeError(f"answer file staged into the jail: {leaked}")
    return JAIL


@criterion
def hidden_lines_match(workspace: Path) -> float:
    """Share of hidden expected lines that match the program's stdout bytes."""
    try:
        expected = (DATA / "hidden_expected.txt").read_bytes()
        stdin_bytes = (DATA / "hidden_inputs.txt").read_bytes()
    except OSError:
        print("hidden_data_unreadable=1")
        return 0.0

    try:
        build = subprocess.run(
            ["go", "build", "-o", "/tmp/titlecase", "."],
            cwd=workspace,
            capture_output=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        print("build_timeout=1")
        return 0.0
    if build.returncode != 0:
        print(f"build_exit={build.returncode}")
        return 0.0

    try:
        jail = _stage_jail(Path("/tmp/titlecase"))
        proc = subprocess.run(
            ["chroot", "--userspec=65534:65534", str(jail), "/titlecase"],
            input=stdin_bytes,
            capture_output=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        print("run_timeout=1")
        return 0.0
    except OSError:
        print("program_start_failed=1")
        return 0.0
    if proc.returncode != 0:
        print(f"program_exit={proc.returncode}")
        return 0.0

    expected_lines = expected.split(b"\n")
    actual_lines = proc.stdout.split(b"\n")
    compared = max(len(expected_lines), len(actual_lines))
    matched = sum(
        1
        for actual, want in zip(actual_lines, expected_lines)
        if actual == want
    )
    print(
        f"matched={matched} expected={len(expected_lines)} actual={len(actual_lines)}"
    )
    if compared == 0:
        return 1.0
    return matched / compared
