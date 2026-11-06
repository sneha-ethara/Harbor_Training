# Titlecase in Go

## 1. What the repository is

This repository is a Python titlecase library released under the MIT License. Its `titlecase` function changes text to Title Caps and lowercases small words. The small words are `a`, `an`, `and`, `as`, `at`, `but`, `by`, `en`, `for`, `if`, `in`, `of`, `on`, `or`, `the`, `to`, `v`, `v.`, `via`, `vs`, and `vs.`, from the New York Times Manual of Style, plus `v` and `vs`. Words are handled in a fixed order, and a word that matches an earlier rule is not processed by later word rules. After the words on a line are handled, a leading small word, a trailing small word, and a small word after a sub-phrase break are capitalized. The Python implementation in this repository is the specification for that behaviour.

## 2. What to build

Build a Go program in `/workspace/repo`. It reads stdin as a sequence of titles, one title per line, and writes the titlecased result to stdout, one title per line. Use the default `titlecase` behaviour: no custom callback, small words at the start and end of a line capitalized, blank lines not preserved, and original space characters kept.

## 3. Hard rules

- Use only the Go standard library. Do not add third-party modules.
- No `.py` file may remain anywhere in the repository when you finish.
- From `/workspace/repo`, `go build ./...` must succeed.

## 4. Behaviour

For every input, the bytes written to stdout must be identical to the string returned by the original Python `titlecase()` for that same input.

## 5. Not checked

Speed, memory use, and the wording of error messages are not checked.

## 6. How it is graded

Hidden automatic tests grade the program. A partial score is possible when some of the required behaviour is correct and some is not.
