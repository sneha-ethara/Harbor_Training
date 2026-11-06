# Repository

This repository contains the Python `titlecase` package, which converts text to title case while applying special handling for small words, punctuation, apostrophe and `Mc` names, honorifics, initials, acronyms, hyphenated and slash-separated words, and line boundaries. Its default small-word list includes words such as “a,” “and,” “of,” and “the”; it also preserves internal capitalization and supports callback-based word overrides. The package is licensed under the MIT License.

# What to build

Build a Go program in `/workspace/repo` that reads one title per line from standard input and prints the titlecased result for each input line on standard output, with one result per line.

# Hard rules

- Use only the Go standard library.
- Leave no `.py` files anywhere under `/workspace/repo`.
- `go build ./...` must pass from `/workspace/repo`.

# Behavior

For every input, the Go program's output must match the original Python `titlecase()` function byte for byte.

# Not checked

Speed, memory usage, and error-message wording are not checked.

# Grading

The work is graded using hidden automatic tests and partial credit.
