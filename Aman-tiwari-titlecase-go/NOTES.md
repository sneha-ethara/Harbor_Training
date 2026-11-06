# NOTES — python-titlecase (source for the `titlecase-go` Harbor task)

## Source

| Item | Value |
|---|---|
| Repo URL | https://github.com/ppannuto/python-titlecase |
| Commit SHA | `42f43e2de55bf003b286c6f8e8d8b2d26676a167` |
| Commit date | 2024-04-05T22:03:59-07:00 |
| Version | 2.4.1 (`titlecase/__init__.py`) |
| Licence | **MIT** (LICENSE.txt, © 2021 Patrick William Pannuto) — allowed |
| Main file | `titlecase/__init__.py` (293 lines), function `titlecase(text)` |

**Which "original"?** The code uses the optional `regex` package if installed, and
falls back to Python's built-in `re` otherwise. `regex` is only an *extra*
(`pip install titlecase[regex]`), so the plain install uses `re`.
**Ground truth for this task = plain install, `REGEX_AVAILABLE = False`, default
arguments** (`titlecase(line)`, no callback, no wordlist file).

## What the repo is (one paragraph)

python-titlecase is a small MIT-licensed Python library (a port of John Gruber's
Perl script) that converts text to Title Case using New York Times style rules.
It capitalises normal words, keeps "small words" (a, an, the, of, …) in lower
case except at the start or end of a title or after a colon/period, and tries to
leave alone things that already look deliberate: mixed-case words (iPhone),
words with inner periods (U.S., example.com), URLs, and initials. It also has
special handling for Mc-names, apostrophe names (O'Neil), hyphenated and
slashed words, honorifics (Mr, Dr), and all-consonant acronyms (BBC).

## Rules (in the order the code applies them, per word)

Each line is split on whitespace; **whitespace is kept exactly** (spaces, tabs).
A line is "all caps" if `line.upper() == line`.

All examples below were produced by running the original code (not guessed).

1. **Normal words → first letter capitalised** (leading punctuation skipped).
   `the lord of the rings` → `The Lord of the Rings`
   `"the quoted title"` → `"The Quoted Title"`
2. **Small words stay lower case** in the middle: a, an, and, as, at, but, by,
   en, for, if, in, of, on, or, the, to, v, v., via, vs, vs.
   `smith vs jones` → `Smith vs Jones`; `smith v. jones` → `Smith v. Jones`
3. **Small word at the start of the line is capitalised** (even after leading punctuation).
   `a tale of two cities` → `A Tale of Two Cities`; `...and then` → `...And Then`
4. **Small word at the end of the line is capitalised** (one trailing punctuation allowed).
   `what are you looking at` → `What Are You Looking At`; `what is it for?` → `What Is It For?`
5. **Small word after `: . ; ? ! -` (and en/em dashes) + a space is capitalised.**
   `star wars: a new hope` → `Star Wars: A New Hope`; `end. the next` → `End. The Next`;
   `war - the sequel` → `War - The Sequel`
6. **Mixed-case words are left alone** (only when the line is not all caps).
   `the iPhone and eBay` → `The iPhone and eBay`; `the NASA mission` → `The NASA Mission`
7. **Words with a letter-period-letter are left alone** (domains, initials).
   `visit example.com today` → `Visit example.com Today`; `a guide to U.S. policy` → `A Guide to U.S. Policy`
8. **All-caps line → words are lowercased first, then titlecased.**
   `NASA LAUNCHES A ROCKET` → `Nasa Launches a Rocket`; `ÉCOLE NORMALE` → `École Normale`
9. **In an all-caps line, initials like `U.S.` are kept.**
   `THE U.S. ARMY` → `The U.S. Army`
10. **Apostrophe after d/o/l: `O'Neil`; but consonant first letter stays lower.**
    `o'neil and d'angelo` → `O'Neil and d'Angelo`; `l'oreal paris` → `l'Oreal Paris`
11. **Mc / MC prefix → `Mc` + titlecased rest.** (`Mac` is NOT special.)
    `mcdonald and macbeth` → `McDonald and Macbeth`; `macbook pro` → `Macbook Pro`; `MC hammer` → `MC Hammer`
12. **Mr / Mrs / Ms / Dr → first letter capitalised.**
    `mr smith and dr jones` → `Mr Smith and Dr Jones`; `dr. who` → `Dr. Who`
13. **Slash words: each part titlecased separately — unless the word has `//`.**
    `input/output errors` → `Input/Output Errors`; `one/two//three` → `One/two//three`
14. **URLs (contain `//`) are not split.**
    `see http://example.com/path` → `See http://example.com/path`
15. **Hyphenated words: each part titlecased separately** (small words inside stay small).
    `a well-known fact` → `A Well-Known Fact`; `in-the-middle` → `In-the-Middle`; `an ode to x-ray` → `An Ode to X-Ray`
16. **All-consonant words longer than 2 letters → ALL CAPS** (y counts as a vowel).
    `the bbc and the nhs` → `The BBC and the NHS`; `psst and hmm` → `PSST and HMM`
17. **All-consonant words of 2 letters or fewer are NOT uppercased.**
    `st louis and the cdc` → `St Louis and the CDC`
18. **Whitespace is preserved exactly.**
    `hello   world\tagain` → `Hello   World\tAgain`
19. **Non-ASCII letters work** (Python `\w` is Unicode).
    `über alles in köln` → `Über Alles in Köln`; `café au lait` → `Café Au Lait` ("au" is not a small word)

## Surprises — cases where my first guess was WRONG (use these as tricky test cases)

- `NASA LAUNCHES A ROCKET` → `Nasa …` — I expected NASA to stay capitals; an all-caps line is lowercased first.
- `psst and hmm` → `PSST and HMM` — the all-consonant rule turns ordinary words into acronyms.
- `l'oreal paris` → `l'Oreal` — the first letter stays lower because `l` is a consonant.
- `one/two//three` → `One/two//three` — the `//` disables slash splitting.
- `café au lait` → `Café Au Lait` — "au" is not in the small-word list.
- `macbook pro` → `Macbook` — only `Mc`, not `Mac`, is special.
- `smith v. jones` → `v.` stays lower — `v.` is a small word.
- `MC hammer` → `MC Hammer` — `MC` on its own is too short for the Mc rule.

## Why porting this to Go is hard

Python's patterns rely on `\b` word boundaries mixed with Unicode `\w`, lazy
`*?` matches, and character classes containing Unicode punctuation (“ ‘ – ‒ — ―).
Go's `regexp` (RE2) has no look-ahead/look-behind or back-references and treats
`\b`/`\w` as ASCII-only, so the rules must be rebuilt by hand with string code.
Small differences only show up on rare inputs (Unicode, apostrophes, `//`, all-caps lines).
