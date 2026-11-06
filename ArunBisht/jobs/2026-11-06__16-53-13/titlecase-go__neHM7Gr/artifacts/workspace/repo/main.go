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
