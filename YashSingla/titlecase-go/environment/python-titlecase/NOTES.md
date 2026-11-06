# Titlecase notes

## License

The project uses the MIT License (MIT), as stated in `LICENSE.txt`.

## Rules applied by `titlecase`

The examples below show the function's behavior with default options unless an option is named.

1. **Use a callback's non-empty result as the word unchanged.** If `callback(word, all_caps=...)` returns a truthy string, that word is accepted verbatim and skipped by subsequent casing rules. Example: with `callback=lambda word, **kwargs: 'iPhone' if word.lower() == 'iphone' else None`, `titlecase('iphone')` → `iPhone`.
2. **Keep dotted uppercase initials intact in an all-uppercase line.** Example: `titlecase('J. R. R. TOLKIEN')` → `J. R. R. TOLKIEN`.
3. **Special-case names beginning with d', l', or o' (including curly apostrophe).** The first letter is uppercased, except a one-letter consonant prefix is lowercased; the letter after the apostrophe is uppercased. Example: `titlecase("o'neill")` → `O'Neill`.
4. **Apply the leading** `Mc` **rule.** A leading `Mc`, `MC`, or `mc` is normalized to `Mc`, and the rest is recursively titlecased. Example: `titlecase('mcdonald')` → `McDonald`.
5. **Capitalize recognized honorifics while preserving the rest of their spelling.** Recognized forms are Mr, Mrs, Ms, and Dr (case-insensitive). Example: `titlecase('mRS smith')` → `MRS Smith`.
6. **Preserve words with an internal period or mixed uppercase letters.** This keeps dotted abbreviations and internal-capital forms as supplied. Example: `titlecase('eBay')` → `eBay`.
7. **Lowercase configured small words.** By default these are `a, an, and, as, at, but, by, en, for, if, in, of, on, or, the, to, v, via, vs` (with optional periods for v/vs). Example: `titlecase('WAR AND PEACE')` → `War and Peace`.
8. **Recursively titlecase slash-separated parts (when there is one slash and not a double slash).** Example: `titlecase('war/peace')` → `War/Peace`.
9. **Recursively titlecase hyphen-separated parts.** Example: `titlecase('state-of-the-art')` → `State-of-the-Art`.
10. **Normalize all-uppercase words before applying ordinary casing.** Example: `titlecase('HELLO')` → `Hello`.
11. **Preserve words made entirely of consonants as uppercase acronyms when longer than two characters.** The consonant set excludes a, e, i, o, u, and y. Example: `titlecase('HTML guide')` → `HTML Guide`.
12. **Capitalize the first letter after leading punctuation for ordinary words.** Example: `titlecase('“hello”')` → `“Hello”`.
13. **Capitalize a small word at the start and end of a line when** `small_first_last=True` **(the default).** Example: `titlecase('the lord of the rings')` → `The Lord of the Rings`.
14. **Capitalize a small word after a colon, semicolon, period, question mark, exclamation mark, or hyphen followed by a space.** Example: `titlecase('one: the sequel')` → `One: The Sequel`.
15. **Handle line breaks according to** `preserve_blank_lines`**.** By default, runs of CR/LF characters are collapsed to one output newline; when true, each CR or LF split is retained. Example: `titlecase('one\n\ntwo', preserve_blank_lines=True)` → `One\n\nTwo`.
16. **Handle whitespace according to** `normalise_space_characters`**.** By default, original whitespace separators are retained; when true, separators are replaced by single ordinary spaces. Example: `titlecase('red\tfox', normalise_space_characters=True)` → `Red Fox`.

A custom small-word pattern can be installed with `set_small_word_list`; for example, after `set_small_word_list('foo')`, `titlecase('FOO BAR')` → `Foo Bar` (restore the default list with `set_small_word_list()` if needed).  
Repository: [https://github.com/ppannuto/python-titlecase](https://github.com/ppannuto/python-titlecase)

Commit: 42f43e2de55bf003b286c6f8e8d8b2d26676a167

Commit date: 2024-04-05T22:03:59-07:00

