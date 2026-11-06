# Titlecase in Go

## 1. What the repository is

This repository is a Python library, released under The MIT License (MIT), whose `titlecase` function converts text to title caps. By default it drops blank lines, keeps the original space characters between words, and writes small words in lowercase. Those small words, from the New York Times Manual of Style plus `v` and `vs`, are: a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, v., via, vs, and vs. A small word is capitalized again when it is the first or last word of a line, or when it follows sub-phrase punctuation (`:`, `.`, `;`, `?`, `!`, or a hyphen or dash) and a space. On an all-uppercase line, runs of initials are left as written and every other word not kept by an earlier rule is lowercased before the remaining rules run. Words of the form `d'…`, `o'…`, or `l'…` keep `d` and `l` lowercase, capitalize `o`, and capitalize the letter after the apostrophe. A `Mc`, `mc`, or `MC` prefix is capitalized and the rest of the word is title-cased. `Mr`, `Mrs`, `Ms`, and `Dr` keep their spelling except that the first letter is uppercase. A word with a period between two letters is left unchanged, as is a word that already contains a capital after other letters when the line is not all uppercase. A word containing `/` but not `//` is split on each slash and each piece is title-cased; a hyphenated word is split the same way. Those pieces do not get the first-word or last-word small-word fix. A word of only consonants longer than two letters is written in uppercase (`a`, `e`, `i`, `o`, `u`, and `y` count as vowels). Any other word has its first letter capitalized, skipping leading punctuation and leaving the rest of the word, including digits, as it is.

## 2. What to build

Build a Go program in `/workspace/repo`. The program reads one title per line from standard input and prints the title-cased result, one per line.

## 3. Hard rules

- Use the Go standard library only.
- When you finish, the repository must contain no `.py` files anywhere.
- `go build ./...` must succeed.

## 4. Behaviour

For every input, the program's output must match the original Python `titlecase()` result byte for byte. Use that function's default arguments.

## 5. Not checked

Speed, memory use, and the wording of error messages are outside the grade.

## 6. How it is graded

Hidden automatic tests grade the program. A partial score is possible.
