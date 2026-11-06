# titlecase-go — a complete Day 3 Harbor task

Port of [`python-titlecase` 2.4.1](https://github.com/ppannuto/python-titlecase)
(MIT, commit `42f43e2`) to Go, built as a graded Harbor task.

The agent only sees `instruction.md` and the container. `solution/`, `tests/`
and `cheat/` stay hidden.

## Layout

```
titlecase-go/
├── instruction.md          # the only file the agent reads
├── task.toml               # author, timeouts, resources, verifier mode
├── .harborignore           # Harbor: keep cheat/screenshot out of run uploads
├── .gitignore              # Harbor packager + git: keep cheat/jobs out of package/push
├── NOTES.md                # Step 1 evidence: SHA, licence, rules, examples
├── environment/
│   ├── Dockerfile          # golang:1.23.12 + the Python repo at /workspace/repo
│   └── repo/               # python-titlecase source (no .git)
├── solution/
│   ├── solve.sh            # writes the Go port, deletes every .py, builds
│   ├── main.go             # verified byte-for-byte port (stdlib only)
│   └── go.mod
├── tests/
│   ├── test.sh             # runs RewardKit
│   ├── build.py            # weight 1
│   ├── no_python.py        # weight 1
│   ├── behaviour.py        # weight 4 (hidden set)
│   ├── reward.toml         # weighted-mean
│   ├── Dockerfile          # verifier: Go + uv + RewardKit baked in
│   ├── gen.py              # regenerates the frozen answer sheets
│   └── data/               # 2000 visible + 2000 hidden input/answer pairs
├── cheat/
│   └── solve.sh            # replays the visible answers (does not port anything)
└── screenshot/             # hand-in proof: one reward image per run
    ├── oracle screenshot.png
    ├── nop screenshot.png
    └── cheat screenshot.png
```

## Expected rewards (verified in real Harbor runs)

| Run | build | no_python | behaviour | reward | job folder |
| --- | --- | --- | --- | --- | --- |
| nothing (`nop`) | 0 | 0 | 0 | **0.0** | `jobs/nop` |
| build only (Python left) | 1 | 0 | 0 | **0.1667** | — |
| cheat (replays visible answers) | 1 | 0 | 0 | **0.1667** | `jobs/cheat` |
| oracle | 1 | 1 | 1.0 | **1.0** | `jobs/oracle3` |

Cheat stays under 0.2 because grading uses the hidden 2000 lines it never saw.
`jobs/oracle3` is the canonical final run (clean repo, no leftover binary);
`jobs/oracle` (0.6667) and `jobs/oracle2` are earlier runs kept for history.

## Regenerating the answer sheets

```powershell
python tests\gen.py --repo environment\repo
```

`gen.py` refuses to run unless the imported `titlecase` is version 2.4.1 on the
stdlib `re` path (`REGEX_AVAILABLE == False`). It always writes the same four
files for seed 1; do not edit `tests/data/*` by hand.

## Commands

```powershell
# once
winget install --id Git.Git -e
winget install --id Docker.DockerDesktop -e
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# new terminal
uv tool install harbor
harbor --version

# from this folder
harbor lint .\titlecase-go
harbor run -p .\titlecase-go -a oracle -o .\jobs --job-name oracle
harbor run -p .\titlecase-go -a nop    -o .\jobs --job-name nop

# cheat check (put the real solution back afterwards)
Copy-Item .\titlecase-go\solution\solve.sh .\titlecase-go\solution\solve.real.sh
Copy-Item .\titlecase-go\cheat\solve.sh    .\titlecase-go\solution\solve.sh -Force
harbor run -p .\titlecase-go -a oracle -o .\jobs --job-name cheat
Move-Item -Force .\titlecase-go\solution\solve.real.sh .\titlecase-go\solution\solve.sh

harbor view .\jobs
```

## Hand-in (Step 8)

Two lines to include with the screenshots:

- **Rules the agent got wrong most:** `d'angelo's` / `o'brien` (the Python code
  intentionally lower-cases the leading consonant), then Mc/MC names, then
  small words after a colon or em dash.
- **What would make it harder:** add a second graded behaviour dimension on a
  fresh mutation-generated hidden set, and a penalty criterion for keeping any
  `.py` file or vendoring a regex library, so "almost right" ports lose the
  free build points.
