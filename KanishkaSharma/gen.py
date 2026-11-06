"""Generate fixed titlecase fixtures from the original Python implementation.

Expected files are produced by calling titlecase(), never by hand.
"""

import random
import sys
from pathlib import Path

# Original checkout named python-titlecase (this task lives inside it).
# "../python-titlecase" from the parent of the task directory.
_TASK = Path(__file__).resolve().parents[1]
_CANDIDATES = [
    (_TASK / ".." / "python-titlecase").resolve(),
    _TASK.parent,
]


def _load_titlecase():
    for repo in _CANDIDATES:
        if (repo / "titlecase" / "__init__.py").is_file():
            sys.path.insert(0, str(repo))
            break
    else:
        raise SystemExit("original python-titlecase checkout not found")
    from titlecase import titlecase

    return titlecase

# Rules from NOTES.md. Small words stay lowercase except where a later rule
# capitalizes them: a, an, and, as, at, but, by, en, for, if, in, of, on, or,
# the, to, v, v., via, vs, vs.
#
# 1. Capitalize the first letter of an ordinary word. Leading punctuation stays.
# 2. Lowercase a small word in the middle of a phrase.
# 3. Capitalize a small word when it is the first or last word of a line.
# 4. Capitalize a small word that starts a sub-phrase after : . ; ? ! or a dash
#    followed by a space.
# 5. Leave a word with an internal period unchanged (domains).
# 6. Leave a mixed-case word unchanged when a later letter is already capital,
#    unless the whole line is uppercase.
# 7. When a whole line is uppercase, lowercase it and titlecase it again.
# 8. On an all-uppercase line, keep a run of initials such as D.C.
# 9. Uppercase an all-consonant word longer than two letters. y counts as a
#    vowel. Shorter ones, such as st, are ordinary words.
# 10. Titlecase each part of a hyphenated word; small words inside stay lower.
# 11. Titlecase each part of a slash-separated word. Do not split //.
# 12. Mc / mc / MC plus at least two characters: capitalize the prefix and
#     titlecase the rest.
# 13. d' / o' / l' (optional 's): capitalize the letter after the apostrophe;
#     capitalize a vowel first letter, leave a non-vowel first letter lower.
# 14. Mr, Mrs, Ms, Dr: uppercase only the first letter.
# 15. Leave a word unchanged when it does not start with a letter (ordinals).
# 16. A callback result is kept as-is. Default titlecase() is what we call.
# 17. Each line is its own title. Blank lines are their own lines here.
# 18. Keep the original space characters between words.

# Input examples from NOTES.md that naive titlecasing gets wrong.
# Outputs are not stored here; titlecase() writes those.
NOTES_EXAMPLES = [
    "the quick brown fox",
    "this vs that",
    "a history of",
    "phrase: a trick",
    "this is just an example.com",
    "iTunes should be unmolested",
    "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    "WASHINGTON, D.C. SHOULD BE FIXED",
    "words with all consonants like cnn",
    "end-to-end",
    "word/word",
    "mcclelland",
    "my name is o'reilly",
    "mr and dr smith",
    "34th 3rd 2nd",
    "a simple udp wrapper",
    "Line number one",
    "and Line three",
    "text\twith\ttabs",
]

NORMAL = [
    "quick", "brown", "fox", "history", "music", "apple", "market", "report",
    "string", "title", "dance", "plane", "force", "case", "problem", "deal",
    "night", "river", "garden", "silver", "public", "office", "winter",
    "summer", "letter", "bridge", "castle", "orange", "yellow", "purple",
    "simple", "wrapper", "thoughts", "repair", "voodoo", "famous", "line",
    "edit", "episode", "harbor", "python", "string", "north", "south",
    "paper", "glass", "stone", "cloud", "field", "coast",
]

SMALL = [
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of",
    "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
]

SPACES = [" ", " ", " ", "\t", "\u00a0", "\u200a", "\u2006"]
BREAKS = [":", ".", ";", "?", "!", "-", "\u2013", "\u2014", "\u2012", "\u2015"]
CONSONANT_ACRONYMS = ["cnn", "bbc", "html", "gmt", "nyc", "ftp"]
SHORT_CONSONANTS = ["st", "tv", "dr"]  # dr is also an honorific when exact
ORDINAL_SUFFIXES = ["th", "rd", "nd", "st"]
INITIALS = ["D.C.", "A.B.", "U.S.", "Ph.D"]


def _word():
    text = random.choice(NORMAL)
    roll = random.randrange(5)
    if roll == 1:
        return text.capitalize()
    if roll == 2:
        return text.upper()
    if roll == 3 and len(text) > 2:
        return text[0] + text[1].upper() + text[2:]
    return text


def _join(parts):
    gap = random.choice(SPACES) if random.random() < 0.25 else " "
    return gap.join(parts)


def _tricky():
    """One fragment that exercises a NOTES.md rule."""
    kind = random.randrange(16)
    if kind == 0:
        return "'" + random.choice(SMALL)
    if kind == 1:
        return random.choice(SMALL)
    if kind == 2:
        return random.choice(NOTES_EXAMPLES)
    if kind == 3:
        return f"{_word()}{random.choice(BREAKS)} {random.choice(SMALL)}"
    if kind == 4:
        return f"{_word()}.{random.choice(['com', 'org', 'io', 'net'])}"
    if kind == 5:
        return random.choice(["iTunes", "AT&T", "OmniFocus", "del.icio.us", "eBay"])
    if kind == 6:
        return random.choice(INITIALS)
    if kind == 7:
        return random.choice(CONSONANT_ACRONYMS + SHORT_CONSONANTS + ["rhythm", "style"])
    if kind == 8:
        return f"{_word()}-{random.choice(SMALL)}-{_word()}"
    if kind == 9:
        if random.random() < 0.4:
            return f"http://{_word()}.com"
        return f"{_word()}/{_word()}"
    if kind == 10:
        return random.choice(["mc", "Mc", "MC"]) + _word()
    if kind == 11:
        stem = _word()
        if random.random() < 0.3:
            stem += "'s"
        return random.choice("dol") + "'" + stem
    if kind == 12:
        return random.choice(["mr", "mrs", "ms", "dr", "Mr", "Mrs", "Ms", "Dr", "MR"])
    if kind == 13:
        number = random.randint(1, 40)
        return f"{number}{random.choice(ORDINAL_SUFFIXES)}"
    if kind == 14:
        return "\t".join(_word() for _ in range(3))
    return f"{_word()}/{random.choice(SMALL)}"


def make_title():
    if random.random() < 0.02:
        return ""
    if random.random() < 0.12:
        core = [random.choice(NOTES_EXAMPLES)]
    else:
        core = [_word() for _ in range(random.randint(2, 5))]
    for _ in range(random.randint(1, 3)):
        core.insert(random.randrange(len(core) + 1), _tricky())
    if random.random() < 0.5:
        core.append(_word())
    line = _join(part for part in core if part != "")
    if random.random() < 0.08:
        return line.upper()
    return line


def _write_pair(inputs_path, expected_path, count, titlecase):
    titles = [make_title() for _ in range(count)]
    # Answers come only from the original function, one call per line.
    expected = [titlecase(title) for title in titles]
    inputs_path.write_text("".join(f"{title}\n" for title in titles), encoding="utf-8", newline="\n")
    expected_path.write_text("".join(f"{line}\n" for line in expected), encoding="utf-8", newline="\n")
    return titles


def main():
    random.seed(1)
    titlecase = _load_titlecase()
    data = Path(__file__).resolve().parent / "data"
    data.mkdir(parents=True, exist_ok=True)
    visible = _write_pair(data / "inputs.txt", data / "expected.txt", 2000, titlecase)
    hidden = _write_pair(data / "hidden_inputs.txt", data / "hidden_expected.txt", 2000, titlecase)
    if visible == hidden:
        raise SystemExit("hidden titles must differ from the visible set")


if __name__ == "__main__":
    main()
