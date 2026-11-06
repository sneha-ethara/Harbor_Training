#!/usr/bin/env python3
"""Generate frozen inputs + expected answers for the titlecase-go task.

The ONLY source of truth for expected output is the original Python
`titlecase` package. This script never invents an answer.

Usage:
    python tests/gen.py
    python tests/gen.py --repo /path/to/python-titlecase
"""

import argparse
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Deterministic corpus. seed(1) -> identical files on every machine/run.
# ---------------------------------------------------------------------------
rng = random.Random(1)

NORMAL = """
the quick brown fox jumps over lazy dog and then runs into forest
harbor agent task model reward trial verifier oracle trajectory rubric judge
build container docker image network allowlist secrets hidden tests solution
write read parse file directory path command output error exit status code
small large fast slow correct broken clean simple complex edge case input
python golang regex string character unicode letter digit punctuation space
project machine sentence title word rule example answer question problem
north south east west river mountain ocean island city village road bridge
morning evening night summer winter spring autumn rain snow wind cloud sun
""".split()

SMALL = "a an and as at but by en for if in of on or the to via vs v".split()

ACRONYMS = [
    "NASA", "FBI", "CIA", "BBC", "IBM", "API", "SDK", "CLI", "GUI", "CPU",
    "GPU", "RAM", "ROM", "SSD", "USB", "HTTP", "HTTPS", "FTP", "SSH", "TCP",
    "UDP", "IP", "DNS", "URL", "JSON", "YAML", "HTML", "CSS", "XML", "SQL",
    "PDF", "PNG", "JPEG", "GIF", "SVG", "MP3", "MP4", "GPS", "NFC", "RFID",
]

CONSONANT_WORDS = ["BBC", "CNN", "NFL", "crypt", "tsk", "hmm", "shh", "psst", "nth", "gym", "myth"]

MIXED = ["iPhone", "eBay", "McDonald", "MacBook", "O'Reilly", "D'Angelo", "L'Oreal", "YouTube", "JavaScript", "GitHub"]

INITIALS = ["U.S.A", "U.S.", "J.R.R.", "A.B.C", "e.g.", "i.e.", "Ph.D.", "M.D."]

NAMES = ["Mr", "Mrs", "Ms", "Dr", "mR", "dR", "MRS", "MS"]

DOTTED = ["example.com", "github.com", "v1.2.3", "3.14", "file.txt", "a.b.c", "node.js"]

APOS = ["don't", "can't", "won't", "it's", "rock'n'roll", "friends'", "o'clock", "ma'am", "y'all", "d'angelo", "l'oreal", "o'brien"]

SLASHED = ["and/or", "TCP/IP", "read/write", "input/output", "a/b/c", "http://x", "//comment"]

HYPHEN = ["state-of-the-art", "mother-in-law", "self-contained", "well-known", "twenty-one", "-leading", "trailing-", "e-mail", "re-run"]

NUMBERS = ["1984", "3rd", "21st", "mp3", "gpt4", "v2", "007", "100%"]

PUNCT_WORDS = ["(hello)", "[test]", '"quoted"', "'single'", "...ellipsis", "end.", "why?", "wow!", "semi;colon", "colon:here", "@handle", "#tag", "$100", "50%", "a_b", "under_score"]

SUBPHRASES = [
    "hello: the world", "stop. the end", "why? because yes", "wow! amazing",
    "wait; the dog", "really- the best", "note: a small word", "end. an example",
    "one: and two", "two: of three", "three: to four", "four: in five",
]

ALL_CAPS_LINES = [
    "THE LORD OF THE RINGS", "NASA AND THE MOON", "U.S.A. IS BIG",
    "J.R.R. TOLKIEN WROTE IT", "THE QUICK BROWN FOX", "A TALE OF TWO CITIES",
]


def random_line() -> str:
    kind = rng.random()
    if kind < 0.10:
        return rng.choice(ALL_CAPS_LINES)
    if kind < 0.18:
        return rng.choice(SUBPHRASES)
    n = rng.randint(2, 8)
    parts = []
    for _ in range(n):
        r = rng.random()
        if r < 0.44:
            w = rng.choice(NORMAL)
        elif r < 0.55:
            w = rng.choice(SMALL)
        elif r < 0.66:
            w = rng.choice(ACRONYMS)
        elif r < 0.72:
            w = rng.choice(CONSONANT_WORDS)
        elif r < 0.78:
            w = rng.choice(MIXED)
        elif r < 0.83:
            w = rng.choice(INITIALS)
        elif r < 0.87:
            w = rng.choice(NAMES)
        elif r < 0.90:
            w = rng.choice(DOTTED)
        elif r < 0.94:
            w = rng.choice(APOS + SLASHED)
        elif r < 0.97:
            w = rng.choice(HYPHEN + NUMBERS)
        else:
            w = rng.choice(PUNCT_WORDS)
        parts.append(w)
    # randomise the space between words (1 or 2 spaces)
    out = parts[0]
    for p in parts[1:]:
        out += ("  " if rng.random() < 0.08 else " ") + p
    return out


def main() -> int:
    task_root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(task_root / "environment" / "repo"),
                    help="path to the original python-titlecase checkout")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "data"))
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo))
    import titlecase  # noqa: E402

    if getattr(titlecase, "__version__", "") != "2.4.1":
        print(f"ERROR: expected titlecase 2.4.1, got {titlecase.__version__}", file=sys.stderr)
        return 1

    # `regex` changes Unicode behaviour; refuse to freeze answers with it loaded.
    if getattr(titlecase, "REGEX_AVAILABLE", False):
        print("ERROR: the `regex` package is installed; expected the stdlib `re` path",
              file=sys.stderr)
        return 1

    lines = []
    seen = set()
    while len(lines) < 4000:
        line = random_line()
        if line and "\n" not in line and "\r" not in line and line not in seen:
            seen.add(line)
            lines.append(line)

    # Guarantee the curated tricky cases land in the corpus.
    for extra in SUBPHRASES + APOS + INITIALS + ["the", "a", "and/or", "state-of-the-art"]:
        if extra not in seen:
            seen.add(extra)
            lines.append(extra)

    visible = lines[:2000]
    hidden = lines[2000:4000]
    rng.shuffle(visible)
    rng.shuffle(hidden)

    expected = [titlecase.titlecase(x) for x in visible]
    hidden_expected = [titlecase.titlecase(x) for x in hidden]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def write(name, rows):
        with open(out / name, "w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(row + "\n")

    write("inputs.txt", visible)
    write("expected.txt", expected)
    write("hidden_inputs.txt", hidden)
    write("hidden_expected.txt", hidden_expected)

    print(f"titlecase version: {titlecase.__version__}")
    print(f"visible: {len(visible)}  hidden: {len(hidden)}")
    print(f"wrote 4 files to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
