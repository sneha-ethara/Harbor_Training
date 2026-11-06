#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO=/workspace/repo

cp "$ROOT/go.mod" "$REPO/go.mod"
cp "$ROOT/main.go" "$REPO/main.go"
cp "$ROOT/titlecase.go" "$REPO/titlecase.go"

find "$REPO" -type f -name '*.py' -delete
rm -rf "$REPO/titlecase"
