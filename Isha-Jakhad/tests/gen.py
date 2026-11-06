"""Generate deterministic titlecase fixtures.

Inputs are synthetic titles. Expected files are the strings returned by the
original python-titlecase ``titlecase()`` for those titles. This script does
not reimplement that function.
"""

import random
import sys
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = TASK_ROOT.parent / "python-titlecase"
DATA_DIR = Path(__file__).resolve().parent / "data"

# The sibling repository is the original package. Importing it from this
# path runs that package's titlecase(), including its own regex fallback.
sys.path.insert(0, str(PACKAGE_ROOT))
from titlecase import titlecase


COUNT = 2000
# 190 yields 11 slots in each 2,000-line set (22 total), one slot more than
# the fixed default examples, so every fixed line is inserted once.
FIXED_STRIDE = 190

# Single-line inputs taken from NOTES.md. Strings that contain a line break
# are omitted here because every fixture line must stay on one line.
CANONICAL = (
    "text\twith\ttabs",
    "my name is o'reilly",
    "oblon, spivak, mcclelland, maier & neustadt",
    "MRS JONES",
    "this is just an example.com",
    "iTunes should be unmolested",
    "this vs. that",
    "word/word",
    "end-to-end",
    "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    "words with all consonants like cnn are acronyms",
    "hello world",
    "'by the Way, small word at the start but within quotes.'",
    "Small word at end is nothing to be afraid of",
    "Starting Sub-Phrase With a Small Word: a Trick, Perhaps?",
    "WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM",
    "a simple tcp and udp wrapper",
    "Line number one",
    "and Line three",
    "THIS IS JUST AN EXAMPLE.COM",
    "St",
)

ORDINARY = (
    "apple", "bridge", "candle", "river", "market", "garden", "silver",
    "window", "letter", "people", "history", "morning", "public", "system",
    "family", "office", "travel", "summer", "winter", "yellow", "purple",
    "strong", "little", "number", "school", "friend", "mother", "father",
    "city", "water", "light", "house", "music", "paper", "story", "group",
    "world", "place", "point", "night", "woman", "child", "state", "month",
    "book", "plant", "table", "stone", "field", "coast", "voice", "image",
    "line", "number", "name", "simple", "wrapper", "problem", "trick",
)

# Documented small-word list, including v / v. / via / vs / vs.
SMALL = (
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
)
SMALL_PLAIN = tuple(word for word in SMALL if "." not in word)

APOS_NAMES = (
    "o'reilly",
    "d'angelo",
    "l'amour",
    "o\u2018brien",
    "d\u2018artagnan",
    "l\u2018etoile",
    "o'reilly's",
    "O'REILLY",
    "d'Arcy",
)
MC_NAMES = (
    "mcclelland", "mcdonald", "mccoy", "mcintyre", "MCDONALD", "McMahon", "MCCOY",
)
HONORIFICS = (
    "m", "mr", "mrs", "ms", "dr", "M", "MR", "MRS", "MS", "DR", "Mr", "Mrs", "Dr",
)
INITIALS = ("D.C.", "U.S.", "A.B", "N.Y.", "U.K.", "A.")
DOTTED = ("example.com", "foo.bar", "news.site", "my.domain")
INTERNAL_CAPS = ("iTunes", "eBay", "iPhone", "macOS", "eBooks")
ACRONYMS = ("cnn", "html", "gps", "bbc", "nfl", "pst")
# Length-2 consonant word documented as staying off the acronym path.
SHORT_CONSONANT = "St"
# Subphrase marks documented in NOTES.md.
SUBPHRASE_MARKS = (":", ".", ";", "?", "!", "-", "\u2013", "\u2012", "\u2014", "\u2015")
TRAILING_PUNCT = (".", ",", "?", "!", "'", ":", ";")
GAPS = ("\t", "\t\t", "  ", "   ", " \t ")


def _words(count):
    return [random.choice(ORDINARY) for _ in range(count)]


def _sentence(count=None):
    if count is None:
        count = random.randint(3, 8)
    return " ".join(_words(count))


def _surround(token):
    left = _words(random.randint(0, 3))
    right = _words(random.randint(0, 3))
    return " ".join(left + [token] + right)


def ordinary_lower():
    return _sentence()


def ordinary_mixed_case():
    words = _words(random.randint(3, 8))
    style = random.randrange(3)
    if style == 0:
        words = [word.capitalize() for word in words]
    elif style == 1:
        words = [word.upper() for word in words]
    else:
        for index in range(0, len(words), 2):
            words[index] = words[index].capitalize()
    return " ".join(words)


def preserved_whitespace():
    parts = _words(random.randint(3, 6))
    pieces = [parts[0]]
    for part in parts[1:]:
        pieces.append(random.choice(GAPS))
        pieces.append(part)
    return "".join(pieces)


def apostrophe_name():
    return _surround(random.choice(APOS_NAMES))


def mc_name():
    if random.randrange(2) == 0:
        return " ".join(
            (
                random.choice(ORDINARY),
                random.choice(ORDINARY) + ",",
                random.choice(MC_NAMES) + ",",
                random.choice(ORDINARY),
                "&",
                random.choice(ORDINARY),
            )
        )
    return _surround(random.choice(MC_NAMES))


def honorific():
    title = random.choice(HONORIFICS)
    name = random.choice(ORDINARY)
    line = f"{title} {name}"
    if random.randrange(2) == 0:
        return line.upper()
    return line


def uppercase_initialism():
    words = [word.upper() for word in _words(random.randint(4, 7))]
    slot = random.randrange(len(words))
    words[slot] = random.choice(INITIALS)
    if random.randrange(2) == 0 and slot != 0:
        words[0] = words[0] + ","
    return " ".join(words)


def dotted_word():
    return _surround(random.choice(DOTTED))


def internal_capitals():
    return _surround(random.choice(INTERNAL_CAPS))


def small_words():
    middle = _words(random.randint(2, 5))
    middle.insert(random.randrange(len(middle) + 1), random.choice(SMALL))
    if random.randrange(2) == 0:
        middle.insert(random.randrange(len(middle) + 1), random.choice(SMALL))
    return " ".join([random.choice(SMALL), *middle, random.choice(SMALL)])


def leading_punctuation():
    return "'" + small_words()


def trailing_punctuation():
    head = " ".join(word.capitalize() for word in _words(random.randint(3, 6)))
    return head + " " + random.choice(SMALL_PLAIN) + random.choice(TRAILING_PUNCT)


def slash_compound():
    if random.randrange(2) == 0:
        token = f"{random.choice(SMALL_PLAIN)}/{random.choice(SMALL_PLAIN)}"
    else:
        token = f"{random.choice(ORDINARY)}/{random.choice(ORDINARY)}"
    return _surround(token)


def hyphen_compound():
    kind = random.randrange(3)
    if kind == 0:
        token = f"{random.choice(ORDINARY)}-{random.choice(SMALL_PLAIN)}-{random.choice(ORDINARY)}"
    elif kind == 1:
        token = f"{random.choice(ORDINARY)}-to-{random.choice(ORDINARY)}"
    else:
        token = "-".join(_words(random.randint(2, 4)))
    return _surround(token)


def all_caps_line():
    return " ".join(word.upper() for word in _words(random.randint(4, 9)))


def consonant_acronym():
    words = _words(random.randint(3, 6))
    words.insert(random.randrange(len(words) + 1), random.choice(ACRONYMS))
    words.insert(random.randrange(len(words) + 1), SHORT_CONSONANT)
    if random.randrange(3) == 0:
        return " ".join(word.upper() for word in words)
    return " ".join(words)


def subphrase():
    left = " ".join(word.capitalize() for word in _words(random.randint(2, 5)))
    mark = random.choice(SUBPHRASE_MARKS)
    small = random.choice(SMALL_PLAIN)
    right = " ".join(_words(random.randint(1, 3)))
    return f"{left}{mark} {small} {right}"


def double_slash():
    token = f"http://{random.choice(DOTTED)}"
    if random.randrange(2) == 0:
        token = f"{random.choice(ORDINARY)}//{random.choice(ORDINARY)}"
    return _surround(token)


def mixed_tricky():
    parts = [
        random.choice(ORDINARY),
        random.choice(ORDINARY),
        "'" + random.choice(SMALL_PLAIN),
        random.choice(APOS_NAMES),
        random.choice(MC_NAMES),
        random.choice(HONORIFICS),
        random.choice(INTERNAL_CAPS),
        random.choice(DOTTED),
        random.choice(ACRONYMS),
        random.choice(SMALL),
        f"{random.choice(ORDINARY)}-{random.choice(SMALL_PLAIN)}-{random.choice(ORDINARY)}",
        f"{random.choice(ORDINARY)}/{random.choice(ORDINARY)}",
    ]
    random.shuffle(parts)
    keep = parts[: random.randint(5, 8)]
    return " ".join(keep)


GENERATORS = (
    ordinary_lower,
    ordinary_mixed_case,
    preserved_whitespace,
    apostrophe_name,
    mc_name,
    honorific,
    uppercase_initialism,
    dotted_word,
    internal_capitals,
    small_words,
    leading_punctuation,
    trailing_punctuation,
    slash_compound,
    hyphen_compound,
    all_caps_line,
    consonant_acronym,
    subphrase,
    double_slash,
    mixed_tricky,
)


def _one_line(text):
    return "\n" not in text and "\r" not in text


def _accept(line, seen):
    if not line or not _one_line(line) or line in seen:
        return False
    result = titlecase(line)
    return isinstance(result, str) and _one_line(result)


def _fixed_slots(count, stride):
    return sum(1 for index in range(count) if index % stride == 0)


def _fill(count, seen, canonical):
    lines = []
    attempts = 0
    while len(lines) < count:
        attempts += 1
        if attempts > count * 50:
            raise RuntimeError(
                f"could not reach {count} unique titles after {attempts} attempts; "
                f"got {len(lines)}"
            )
        if canonical and len(lines) % FIXED_STRIDE == 0:
            raw = canonical.pop(0)
            if not raw or not _one_line(raw):
                raise RuntimeError("fixed input contains an embedded line break or is empty")
            result = titlecase(raw)
            if not isinstance(result, str) or not _one_line(result):
                raise RuntimeError(
                    "default titlecase() did not return one line for a fixed input"
                )
            if raw in seen:
                raise RuntimeError("fixed input was already used")
            seen.add(raw)
            lines.append(raw)
            continue
        raw = GENERATORS[len(lines) % len(GENERATORS)]()
        if raw in seen or raw in canonical:
            continue
        if _accept(raw, seen):
            seen.add(raw)
            lines.append(raw)
    return lines


def _write_lines(path, lines):
    if len(lines) != COUNT:
        raise RuntimeError(f"{path.name} has {len(lines)} lines, expected {COUNT}")
    for line in lines:
        if not _one_line(line):
            raise RuntimeError(f"{path.name} contains an embedded line break")
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def _expected(lines):
    expected = []
    for line in lines:
        result = titlecase(line)
        if not isinstance(result, str) or not _one_line(result):
            raise RuntimeError("original titlecase() did not return one line")
        expected.append(result)
    return expected


def main():
    random.seed(1)
    if not PACKAGE_ROOT.is_dir():
        raise RuntimeError(f"original package not found: {PACKAGE_ROOT}")

    slots = _fixed_slots(COUNT, FIXED_STRIDE) * 2
    if slots < len(CANONICAL):
        raise RuntimeError(
            f"{slots} fixed-input slots for {len(CANONICAL)} documented default examples"
        )

    seen = set()
    canonical = list(CANONICAL)
    visible = _fill(COUNT, seen, canonical)
    hidden = _fill(COUNT, seen, canonical)
    if canonical:
        raise RuntimeError(f"{len(canonical)} fixed inputs were not inserted")
    if set(visible) & set(hidden):
        raise RuntimeError("visible and hidden inputs overlap")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _write_lines(DATA_DIR / "inputs.txt", visible)
    _write_lines(DATA_DIR / "hidden_inputs.txt", hidden)
    _write_lines(DATA_DIR / "expected.txt", _expected(visible))
    _write_lines(DATA_DIR / "hidden_expected.txt", _expected(hidden))


if __name__ == "__main__":
    main()
