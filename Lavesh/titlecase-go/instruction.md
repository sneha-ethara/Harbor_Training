# Titlecase in Go

## Repository

`/workspace/repo` is the Python project python-titlecase.

## What to build

Build a Go program in `/workspace/repo`. `go.mod` and `package main` must be at the repository root so that `go build -o titlecase .` works. The program reads one title per line from stdin (UTF-8) and prints the titlecased result, one line per input line, each followed by a newline. An empty input line produces an empty output line.

## Hard rules

Use only the Go standard library. When you finish, no `.py` file may remain anywhere in the repository. `go build ./...` must pass.

## Behaviour

For every input, the output must match the original Python `titlecase()` function, called with its default arguments and without the optional `regex` package installed, byte for byte.

## Not checked

Speed, memory, and error-message wording are not checked.

## Grading

Hidden automatic tests grade the program. The score can be partial.
