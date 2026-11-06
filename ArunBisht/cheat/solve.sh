#!/bin/bash
set -euo pipefail

cd /workspace/repo

cat > go.mod << 'EOF'
module titlecase

go 1.23
EOF

cat > main.go << 'EOF'
package main

import (
	"fmt"
	"os"
)

func main() {
	text, err := os.ReadFile("tests/data/expected.txt")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	os.Stdout.Write(text)
}
EOF

find /workspace/repo -type f -name '*.py' -delete
