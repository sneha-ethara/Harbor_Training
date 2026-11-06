# Titlecase notes

## Licence

The MIT License (MIT)

## Rules applied by `titlecase`

1. The function splits the text on line breaks. By default a run of breaks counts as one break, so blank lines are dropped. With `preserve_blank_lines=True`, every break is kept, including blank lines. Processed lines are joined with `\n`.
   - Input: `Line number one\n\nand Line three\n`
   - Output: `Line Number One\nAnd Line Three\n`

2. Each line is split into words on whitespace. The original space characters (spaces, tabs, and other space characters) are put back between the words. With `normalise_space_characters=True`, the words are joined with a single ordinary space instead.
   - Input: `text\twith\ttabs`
   - Output: `Text\tWith\tTabs`

3. If a `callback` is given and it returns a non-empty value for a word, that value is used as the word. The result is left unchanged by every later rule, including the first-word and last-word small-word fixes.
   - Input: `at&t` with a callback that returns `AT&T` for that word
   - Output: `AT&T`

4. When the whole line is uppercase, a word that is a run of initials (an uppercase letter and a period, such as `A.B` or `A.B.`) is left as written.
   - Input: `A.B. MEETING`
   - Output: `A.B. Meeting`

5. A word shaped like `d'…`, `o'…`, or `l'…` (straight or curly apostrophe, optional trailing `'s`) keeps that shape: `d` and `l` stay lowercase, `o` is capitalized, and the letter after the apostrophe is capitalized.
   - Input: `l'grange`
   - Output: `l'Grange`

6. A word that starts with `Mc`, `mc`, or `MC` and then more letters has that prefix capitalized, and the remainder is title-cased on its own.
   - Input: `oblon, spivak, mcclelland, maier & neustadt`
   - Output: `Oblon, Spivak, McClelland, Maier & Neustadt`

7. The words `Mr`, `Mrs`, `Ms`, and `Dr`, in any case, are kept as written except that the first letter is forced to uppercase.
   - Input: `Mr McTavish went to MacDonalds`
   - Output: `Mr McTavish Went to MacDonalds`

8. A word with a period between two letters (a hostname, `D.C.`, and similar) is left unchanged.
   - Input: `this is just an example.com`
   - Output: `This Is Just an example.com`

9. When the line is not entirely uppercase, a word that already contains a capital after other letters (for example `iTunes` or `AT&T`) is left unchanged.
   - Input: `iTunes should be unmolested`
   - Output: `iTunes Should Be Unmolested`

10. Small words are written in lowercase. The list, from the New York Times Manual of Style plus `vs` and `v`, is: a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, v., via, vs, vs.
    - Input: `this vs that`
    - Output: `This vs That`

11. A word that contains `/` but not `//` is split on each slash. Each piece is title-cased on its own, without the first-word and last-word small-word fixes, and the slashes are kept. A `//`, as in a URL, is not split.
    - Input: `word/word`
    - Output: `Word/Word`

12. A word that contains `-` is split on each hyphen. Each piece is title-cased on its own, without the first-word and last-word small-word fixes, and the hyphens are kept.
    - Input: `a-b end-to-end two-not-three/three-by-four/five-and`
    - Output: `A-B End-to-End Two-Not-Three/Three-by-Four/Five-And`

13. On a line that is entirely uppercase, a word that was not kept by an earlier rule is lowercased before the remaining rules run, so it can be capitalized normally.
    - Input: `THIS IS ALL CAPS AND SHOULD BE ADDRESSED`
    - Output: `This Is All Caps and Should Be Addressed`

14. A word made only of consonants, longer than two letters, is treated as an acronym and written in uppercase. `a`, `e`, `i`, `o`, `u`, and `y` count as vowels, so a short word such as `St` is not treated as an acronym.
    - Input: `Words with all consonants like cnn are acronyms`
    - Output: `Words With All Consonants Like CNN Are Acronyms`

15. Any other word has its first letter capitalized. Leading punctuation is skipped, and the rest of the word is left as it is, so digits and ordinals such as `2nd` stay put.
    - Input: `34th 3rd 2nd`
    - Output: `34th 3rd 2nd`

16. With `small_first_last` left at its default, a small word at the start of the line is capitalized, including when punctuation precedes it. This step is skipped for a word frozen by a callback, and it is not applied inside a slash- or hyphen-split piece.
   - Input: `a thing`
   - Output: `A Thing`

17. With `small_first_last` left at its default, a small word at the end of the line is capitalized, including one trailing punctuation mark. The same exceptions as the first-word rule apply.
    - Input: `Small word at end is nothing to be afraid of`
    - Output: `Small Word at End Is Nothing to Be Afraid Of`

18. After the line is joined, a small word that comes right after sub-phrase punctuation and a space is capitalized. The punctuation is `:`, `.`, `;`, `?`, `!`, or a hyphen or dash (`-`, `–`, `‒`, `—`, `―`).
    - Input: `Starting Sub-Phrase With a Small Word: a Trick, Perhaps?`
    - Output: `Starting Sub-Phrase With a Small Word: A Trick, Perhaps?`
