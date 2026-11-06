# NOTES.md

## 1. Project Information

- Project: python-titlecase
- Version: 2.4.1
- Original implementation: titlecase/__init__.py
- Original repository: https://github.com/ppannuto/python-titlecase
- Purpose: Convert text into title case while applying special capitalisation rules.

## 2. Licence

- Licence: MIT License
- Copyright: (c) 2021 Patrick William Pannuto
- Licence file: environment/python-titlecase/LICENSE.txt

## 3. Original Release Information

- Original repository: https://github.com/ppannuto/python-titlecase
- Release: v2.4.1
- Official release commit SHA: 418c57ca6c7f324ddc2813b3fc88d52e84db63bd
- Release commit date: 2023-09-23
- Commit message: v2.4.1
- Commit URL: https://github.com/ppannuto/python-titlecase/commit/418c57ca6c7f324ddc2813b3fc88d52e84db63bd

Note: The local environment/python-titlecase directory does not contain its own Git metadata. Therefore, the SHA above identifies the official v2.4.1 release commit, not a verified local checkout SHA.

## 4. Titlecase Rules

The following rules are derived from the original Python implementation.

### Rule 1: Small Words

Common words such as a, an, and, as, at, but, by, for, in, of, on, or, the and to are normally kept lowercase inside a title.

- Input: war and peace
- Output: War and Peace

### Rule 2: First and Last Words

Small words at the beginning and end of a title are capitalised.

- Input: a journey through the history of
- Output: A Journey Through the History Of

### Rule 3: Preserve Existing Internal Capitalisation

Words containing internal uppercase letters are preserved.

- Input: using an iPhone
- Output: Using an iPhone

### Rule 4: Acronyms

Words consisting entirely of consonants and containing more than two characters are capitalised as acronyms.

- Input: fbi and nypd
- Output: FBI and NYPD

### Rule 5: Apostrophe Names

Special handling is applied to names such as d'Artagnan and O'Reilly.

- Input: d'artagnan and o'reilly
- Output: d'Artagnan and O'Reilly

### Rule 6: Mc Names

Names beginning with Mc receive special internal capitalisation.

- Input: mcdonald meets mckenzie
- Output: McDonald Meets McKenzie

### Rule 7: Punctuation Subphrases

Small words following qualifying punctuation and a space are capitalised.

- Input: war and peace: a new perspective
- Output: War and Peace: A New Perspective

### Rule 8: Hyphenated Words

Hyphen-separated parts are recursively title-cased.

- Input: the art-of-building software
- Output: The Art-of-Building Software

### Rule 9: Slash-Separated Words

Slash-separated parts are recursively title-cased.

- Input: science/technology and research
- Output: Science/Technology and Research

### Rule 10: Custom Wordlist Callback

A callback can preserve configured capitalisation for specific words.

- Wordlist entry: NASA
- Input: working with nasa
- Expected output: Working with NASA

## 5. Independent Python Verification

The original Python implementation was imported and tested locally.

| No. | Input | Actual Output | Result |
|---|---|---|---|
| 1 | a journey through the history of india | A Journey Through the History of India | Passed |
| 2 | war and peace: a new perspective | War and Peace: A New Perspective | Passed |
| 3 | the art-of-building software | The Art-of-Building Software | Passed |

Total: 3 examples passed, 0 failed.

## 6. Go Implementation Verification

The Go implementation was tested locally using pytest.

- Test command: python -m pytest .\tests\test_outputs.py -v
- Total tests: 141
- Passed: 141
- Failed: 0
- Execution time: 27.27 seconds

## 7. Existing Project Commit Information

- Commit SHA: 879f1285e2e9e143b71720886b22aa6049d7bcf5
- Commit date: 2026-11-06 17:48:21 +0530
- Commit message: Move titlecase task under contributor folder
