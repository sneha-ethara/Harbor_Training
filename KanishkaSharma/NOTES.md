# Titlecase notes
Project: python-titlecase
Repository: https://github.com/ppannuto/python-titlecase
Commit SHA: 42f43e2de55bf003b286c6f8e8d8b2d26676a167 2024-04-05T22:03:59-07:00

## Licence

The MIT License (MIT)

## Rules

`titlecase` turns each word into title caps, then applies the rules below. Small words, left lowercase except where a later rule says otherwise, are: a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, v., via, vs, and vs.

1. Capitalize the first letter of an ordinary word. Leading punctuation stays in place, and the first letter after it is the one that is capitalized.
   - Input: `the quick brown fox`
   - Output: `The Quick Brown Fox`

2. Lowercase a small word in the middle of a phrase.
   - Input: `this vs that`
   - Output: `This vs That`

3. Capitalize a small word when it is the first or last word of a line.
   - Input: `a history of`
   - Output: `A History Of`

4. Capitalize a small word that starts a new sub-phrase. The break is a colon, period, semicolon, question mark, exclamation mark, or dash, followed by a space.
   - Input: `phrase: a trick`
   - Output: `Phrase: A Trick`

5. Leave a word unchanged when it contains an internal period (a letter, a period, and another letter), such as a domain name.
   - Input: `this is just an example.com`
   - Output: `This Is Just an example.com`

6. Leave a mixed-case word unchanged when it already has a capital later in the word, as long as the whole line is not uppercase.
   - Input: `iTunes should be unmolested`
   - Output: `iTunes Should Be Unmolested`

7. When a whole line is uppercase, lowercase its words and titlecase them again.
   - Input: `THIS IS ALL CAPS AND SHOULD BE ADDRESSED`
   - Output: `This Is All Caps and Should Be Addressed`

8. On an all-uppercase line, keep a run of initials (such as `D.C.`) as it is.
   - Input: `WASHINGTON, D.C. SHOULD BE FIXED`
   - Output: `Washington, D.C. Should Be Fixed`

9. Uppercase a word made only of consonants when it is longer than two letters. `y` counts as a vowel, so it blocks this rule. Shorter consonant words, such as `st`, are titlecased as ordinary words.
   - Input: `words with all consonants like cnn`
   - Output: `Words With All Consonants Like CNN`

10. Titlecase each part of a hyphenated word on its own, and leave a small word inside the compound lowercase.
    - Input: `end-to-end`
    - Output: `End-to-End`

11. Titlecase each part of a slash-separated word on its own. A double slash is not split, so a URL stays one word and the internal-period rule can keep it unchanged.
    - Input: `word/word`
    - Output: `Word/Word`

12. For a word that starts with `Mc`, `mc`, or `MC` and has at least two characters after that prefix, capitalize the prefix and titlecase the rest.
    - Input: `mcclelland`
    - Output: `McClelland`

13. For a word shaped like `d'…`, `o'…`, or `l'…` (optionally ending in `'s`), capitalize the letter after the apostrophe. Capitalize the first letter when it is a vowel, and leave it lowercase when it is not.
    - Input: `my name is o'reilly`
    - Output: `My Name Is O'Reilly`

14. For the exact words `Mr`, `Mrs`, `Ms`, and `Dr` in any case, uppercase only the first letter and leave the rest as written.
    - Input: `mr and dr smith`
    - Output: `Mr and Dr Smith`

15. Leave a word unchanged when it does not start with a letter (punctuation before the word does not count), including ordinals such as `34th`.
    - Input: `34th 3rd 2nd`
    - Output: `34th 3rd 2nd`

16. If a callback returns a new word, use that word and do not apply any further rule to it, including the first-word and last-word capitalization.
    - Input: `a simple udp wrapper` with a callback that returns `UDP` for that word
    - Output: `A Simple UDP Wrapper`

17. Process each line on its own and join the results with newlines. Consecutive blank lines are dropped unless `preserve_blank_lines` is set.
    - Input: `Line number one` followed by a blank line and `and Line three`
    - Output: `Line Number One` followed by `And Line Three` (the blank line is gone)

18. Keep the original space characters between words. If `normalise_space_characters` is set, every space character becomes a normal space.
    - Input: `text`, a tab, `with`, a tab, `tabs`
    - Output: `Text`, a tab, `With`, a tab, `Tabs`
