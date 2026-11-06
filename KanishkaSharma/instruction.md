# Titlecase in Go

## 1. What the repository is

This repository is python-titlecase (https://github.com/ppannuto/python-titlecase) at commit 42f43e2de55bf003b286c6f8e8d8b2d26676a167 (2024-04-05T22:03:59-07:00), released under the MIT License. Its `titlecase` function turns each word into title caps, then applies a fixed set of rules. Small words, left lowercase except where a later rule says otherwise, are: a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, v., via, vs, and vs. Those rules are written up in `NOTES.md` and implemented by the Python `titlecase` function already in the tree.

## 2. What to build

Build a Go program in `/workspace/repo`. It reads one title per line from standard input and prints the titlecased result, one per line.

## 3. Hard rules

- Use only the Go standard library.
- No `.py` files may be left anywhere in the repository.
- `go build ./...` must pass.

## 4. Behaviour

The output must match the original Python `titlecase()` byte for byte, for every input.

## 5. Not checked

Speed, memory, and error-message wording are not checked.

## 6. How it is graded

Grading is hidden automatic tests. A partial score is possible.
