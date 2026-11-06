#!/bin/bash
# Reference solution (the oracle): write the verified Go port, remove every
# Python source file, and prove the module builds offline.
set -euo pipefail

REPO=/workspace/repo

cp /solution/go.mod  "$REPO/go.mod"
cp /solution/main.go "$REPO/main.go"

# The task requires the Python implementation to be gone.
find "$REPO" -type f -name '*.py' -delete
find "$REPO" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true

# Drop the now-empty package directory: a bare `go build ./...` would otherwise
# fail because it tries to write its `titlecase` binary over that directory.
rmdir "$REPO/titlecase" 2>/dev/null || true

cd "$REPO"
GOTOOLCHAIN=local go build ./...
rm -f "$REPO/titlecase"   # do not ship the compiled binary in the artifact
