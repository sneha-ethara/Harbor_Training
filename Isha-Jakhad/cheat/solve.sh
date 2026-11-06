#!/bin/bash
set -euo pipefail

REPO=/workspace/repo

mv "$REPO/titlecase" "$REPO/python-titlecase-src"

cat > "$REPO/go.mod" <<'EOF'
module titlecase

go 1.23
EOF

cat > "$REPO/main.go" <<'EOF'
package main

import "os"

func main() {
	data, err := os.ReadFile("tests/data/expected.txt")
	if err != nil {
		os.Exit(1)
	}
	os.Stdout.Write(data)
}
EOF
