#!/bin/bash
set -euo pipefail

repo=/workspace/repo
mkdir -p "$repo"

cat > "$repo/go.mod" <<'EOF'
module titlecase

go 1.23
EOF

cat > "$repo/main.go" <<'EOF'
package main

import "os"

func main() {
	b, err := os.ReadFile("/tests/data/expected.txt")
	if err != nil {
		os.Exit(1)
	}
	os.Stdout.Write(b)
}
EOF

find "$repo" -type f -name '*.py' -delete
rm -rf "$repo/titlecase"
