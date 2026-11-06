# NOTES — python-titlecase (source of truth)

- Repository: https://github.com/ppannuto/python-titlecase
- Commit (main): `42f43e2de55bf003b286c6f8e8d8b2d26676a167`
- Commit date: 2024-04-06T05:03:59Z
- Version: 2.4.1 (`titlecase/__init__.py`)
- Licence: **MIT** (see `LICENSE.txt`)
- Runtime used to freeze answers: Python 3.12.8, stdlib `re` path
  (`regex` is NOT installed, so `REGEX_AVAILABLE = False`)

## What it does

`titlecase(text)` splits text into lines, then into words and the whitespace
between them, applies a fixed chain of rules to every word, then fixes the first
and last word of each line and small words that start a sub-phrase.

## Rules, in the order the code applies them

1. **All-caps lines keep their initials.** In a line where
   `line.upper() == line`, a word that is only initials is left alone.
   `U.S.A` → `U.S.A`, `J.R.R.` → `J.R.R.`
2. **d'/o'/l' names.** `^[dol]['‘]\w+...$` capitalises the letter after the
   apostrophe. `o'brien` → `O'Brien`, `d'angelo's` → `d'Angelo's` (the leading
   consonant is deliberately lower-cased by the code — a real quirk).
3. **Mc / MC names.** `Mc`/`MC` followed by 2 or more characters **inside the
   same word** is split and the rest is titlecased. `mcdonald's` → `McDonald's`.
   (`MC Hammer` is two words, so it is left unchanged.)
4. **Honorifics.** Exactly `mr`, `mrs`, `ms`, `dr` (any case) become
   `Mr`, `Mrs`, `Ms`, `Dr`.
5. **Dotted words are left alone.** Any `word.word` is untouched.
   `example.com` → `example.com`, `v1.2.3` → `v1.2.3`.
6. **Inner capitals are left alone.** A word with a lower-case run followed by
   an upper-case run is untouched. `iPhone`, `eBay`, `JavaScript`.
7. **Small words.** `a an and as at but by en for if in of on or the to v v. via
   vs vs.` are lower-cased in the middle. `the lord of the rings` →
   `The Lord of the Rings`.
8. **Slashes.** A word with `/` (but not `//`) is titlecased part by part.
   `read/write` → `Read/Write`; `TCP/IP` → `TCP/Ip` (the 2-letter `IP` is too
   short to become an acronym); in a sentence, `a title and/or string` →
   `A Title and/or String`.
9. **Hyphens.** Each hyphen-separated part is titlecased with the
   small-first/last rule disabled. `state-of-the-art` → `State-of-the-Art`,
   `mother-in-law` → `Mother-in-Law`.
10. **All-caps words are lower-cased first**, then normal capitalisation is
    applied. `THE LORD OF THE RINGS` → `The Lord of the Rings`.
11. **All-consonant words longer than 2 letters are acronyms.** `y` counts as a
    vowel for this check. `cnn` → `CNN`, `tsk` → `TSK`; `crypt` → `Crypt` (it
    contains `y`), and `st` stays `St` (2 letters).
12. **Otherwise capitalise the first letter.** Leading punctuation is skipped.
    `(hello)` → `(Hello)`.
13. **First and last word of a line.** A small word at the start or end is
    capitalised. `small word at end is nothing to be afraid of` →
    `Small Word at End Is Nothing to Be Afraid Of`; `'by the way ...'` →
    `'By the Way ...'`.
14. **Sub-phrase after punctuation.** After `: ; . ? ! -` + one space, a small
    word is capitalised. `hello: the world` → `Hello: The World`,
    `wait; the dog` → `Wait; The Dog`, `really- the best` → `Really- The Best`.

## Verified examples (produced by running the Python code)

| Input | Output |
| --- | --- |
| `the lord of the rings` | `The Lord of the Rings` |
| `THE LORD OF THE RINGS` | `The Lord of the Rings` |
| `this is a TEST` | `This Is a TEST` |
| `small word at end is nothing to be afraid of` | `Small Word at End Is Nothing to Be Afraid Of` |
| `state-of-the-art` | `State-of-the-Art` |
| `a title and/or string` | `A Title and/or String` |
| `mcdonald's restaurant` | `McDonald's Restaurant` |
| `J.R.R. Tolkien wrote it` | `J.R.R. Tolkien Wrote It` |
| `example.com is down` | `example.com Is Down` |
| `d'angelo's pizza` | `d'Angelo's Pizza` |
| `hello: the world` | `Hello: The World` |
| `Dr and Mrs Smith met Mr Jones` | `Dr and Mrs Smith Met Mr Jones` |
| `the 3rd 2nd and 34th` | `The 3rd 2nd and 34th` |
| `iPhone and eBay and McDonald` | `iPhone and eBay and McDonald` |
| `this v. that vs. the other` | `This v. That vs. The Other` |

## Why this is a hard port (answer for the hand-in)

Go's `regexp` (RE2) has no look-ahead, look-behind or back-references, and its
`\w` / `\b` are ASCII-only. The Python version leans on `\w` inside
`CAPFIRST`, `INLINE_PERIOD`, `APOS_SECOND` and `MAC_MC`, so those checks had to
be re-implemented by hand over runes, not copied as regular expressions.
The subtle traps are the *order* of the rules, the greedy/non-greedy matches,
the `str.capitalize()` semantics (first letter up, everything else down), and
sub-phrase handling inside ordinary words.

## Frozen answer sheet

`tests/gen.py` (seed 1) produced:

- `tests/data/inputs.txt` + `expected.txt` — 2000 visible pairs
- `tests/data/hidden_inputs.txt` + `hidden_expected.txt` — 2000 hidden pairs

Answers were produced only by running `titlecase.titlecase()` on each line; no
answer was written by hand. Re-running `gen.py` produces byte-identical files.
