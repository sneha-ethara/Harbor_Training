# day3/titlecase-go

A Harbor task: port **python-titlecase** (v2.4.1, MIT,
commit `42f43e2de55bf003b286c6f8e8d8b2d26676a167`) to Go with byte-identical
output, then remove the Python code.

## Results (Harbor 0.25.0, local Docker)

| Run | Command | build (w1) | no_python (w1) | behaviour (w4) | **reward** |
|---|---|---|---|---|---|
| Oracle | `harbor run -p ./titlecase-go -a oracle` | 1.0 | 1.0 | 1.0 | **1.0** |
| Nop | `harbor run -p ./titlecase-go -a nop` | 0.0 | 0.0 | 0.0 | **0.0** |
| Cheat (`cheat/solve.sh` swapped in) | `harbor run -p ./titlecase-go -a oracle` | 1.0 | 0.0 | 0.0 | **0.167** |

## Hand-in notes

**Rules that were hardest to get right:** the oracle port matched 2000/2000
visible lines on the first build, so there was no single rule it kept getting
wrong. The rules that needed the most care were the ones Go's regexp can't copy
directly: Unicode `\b`/`\w` word boundaries (SMALL_FIRST / SMALL_LAST), the
case-sensitive SUBPHRASE rule with no `\b` (which also capitalises a prefix like
`by` in `byte.com`), the `_`-is-both-punctuation-and-a-word-char trap in
CAPFIRST, all-caps-line detection with Python's full `upper()` (`ß` → `SS`),
and the recursive calls for Mc-names, hyphens and slashes.

**To make it harder:** right now 2 of 6 points (build + no_python) go to any Go
program that builds once the `.py` files are gone, even one that does no
titlecasing (measured: 0.33). Tie those points to behaviour (for example, only
pay them when behaviour ≥ 0.5), and add more hidden lines on the rare paths
(`_`-prefixed words, `v.` before a separator, Greek final sigma, `ſ`/Kelvin-sign
case folding, `\x1c`–`\x1f` whitespace).

## Layout

```
instruction.md          what the agent sees
task.toml               1 CPU / 2 GB, agent: user "agent", no internet;
                        verifier: separate container, PyPI only
environment/Dockerfile  golang:1.23 + the original repo at /workspace/repo
solution/solve.sh       oracle: writes go.mod + main.go, deletes all Python
cheat/solve.sh          prints the VISIBLE answers; used only to test the tests
tests/Dockerfile        verifier image: python 3.12 + golang 1.23, /tests root-only
tests/test.sh           uvx harbor-rewardkit -> /logs/verifier/reward.json
tests/reward.toml       weighted-mean: build 1, no_python 1, behaviour 4
tests/{build,no_python,behaviour}/  one check per folder = one score each
tests/gen.py            random.seed(1); 2000 visible + 2000 hidden titles (no overlap);
                        mixes normal words, every NOTES.md example, Unicode,
                        AT&T/Q&A, ordinals, tab / no-break / em-space whitespace;
                        answers produced by the ORIGINAL Python titlecase()
tests/data/             inputs/expected (visible) + hidden_inputs/hidden_expected
```

## Anti-cheating

- Tests run in a **separate container**; the agent never sees `tests/` or `solution/`.
- Agent has **no internet** (allowlist, empty) and runs as a **non-root user**.
- Behaviour is graded on the **hidden** set only.
- The agent's program runs as user `runner`, who **cannot read `/tests`**: a
  program that tries to open the hidden answers gets behaviour 0 (tested).
