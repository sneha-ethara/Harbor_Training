"""Generate fixed titlecase inputs and expected outputs.

Expected lines are produced only by calling the original Python titlecase().
"""

import random
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
COUNT = 2000

# Normal words mixed into every title.
NORMAL = [
    "apple", "bridge", "castle", "dance", "engine", "forest", "garden",
    "harbor", "island", "journey", "king", "light", "music", "night",
    "ocean", "paper", "quest", "river", "stone", "tower", "umbrella",
    "valley", "winter", "yellow", "market", "history", "science", "picture",
    "silver", "golden", "quiet", "public", "final", "open", "secret",
    "north", "south", "early", "late", "wild", "calm", "brief", "grand",
]

# Small words from NOTES.md (New York Times list, plus v and vs).
SMALL = [
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
]

# Single-line tricky inputs copied from NOTES.md. Blank-line examples are
# omitted here because each generated record must stay on one line.
NOTES_EXAMPLES = [
    "text\twith\ttabs",
    "a simple tcp and udp wrapper",
    "WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM",
    "my name is o'reilly",
    "l'grange",
    "oblon, spivak, mcclelland, maier & neustadt",
    "mr mrs ms dr",
    "this is just an example.com",
    "iTunes should be unmolested",
    "this v that",
    "a title and/or string",
    "end-to-end",
    "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    "Words with all consonants like cnn are acronyms",
    "hello world",
    "34th 3rd 2nd",
    "a thing",
    "Small word at end is nothing to be afraid of",
    "Starting Sub-Phrase With a Small Word: a Trick, Perhaps?",
]

# Tokens that exercise the same rules as those examples.
TRICKY_TOKENS = [
    "o'reilly", "o'grange", "o'grange's", "l'grange", "l'amour",
    "d'artagnan", "l\u2018grange", "o\u2018reilly",
    "mcclelland", "mccarthy", "mcfoo", "McTavish", "MCFOO", "MacDonalds",
    "mr", "mrs", "ms", "dr",
    "example.com", "del.icio.us", "http://foo.com",
    "iTunes", "OmniFocus", "AT&T", "Q&A",
    "cnn", "html", "gps", "bbc", "sql", "st",
    "34th", "3rd", "2nd", "5th",
    "end-to-end", "a-b", "five-and", "two-not-three",
    "and/or", "word/word",
    "D.C.", "A.B.",
]

SPACES = [" ", "\t", "\u00a0", "\u200a", "\u2006"]
SUBPHRASE_MARKS = [":", ".", ";", "?", "!", "-", "\u2013", "\u2012", "\u2014", "\u2015"]


def _words(n):
    return [random.choice(NORMAL) for _ in range(n)]


def _sprinkle(words):
    for i in range(len(words)):
        if random.random() < 0.55:
            words[i] = random.choice(TRICKY_TOKENS + SMALL)
    if random.random() < 0.3:
        words[0] = random.choice(SMALL)
    if random.random() < 0.3:
        words[-1] = random.choice(SMALL)
    return words


def _with_subphrase(words):
    mark = random.choice(SUBPHRASE_MARKS)
    cut = random.randint(1, len(words) - 1)
    left = " ".join(words[:cut])
    right = words[cut:]
    right[0] = random.choice(SMALL)
    return left + mark + " " + " ".join(right)


def make_title():
    """One title: ordinary words mixed with a NOTES.md tricky case."""
    roll = random.random()
    if roll < 0.18:
        example = random.choice(NOTES_EXAMPLES)
        prefix = " ".join(_words(random.randint(0, 3)))
        suffix = " ".join(_words(random.randint(0, 2)))
        parts = [part for part in (prefix, example, suffix) if part]
        return " ".join(parts)

    words = _sprinkle(_words(random.randint(4, 10)))
    if roll < 0.40:
        return _with_subphrase(words)
    if roll < 0.55:
        return random.choice(SPACES).join(words)
    if roll < 0.72:
        if random.random() < 0.4:
            words.insert(random.randrange(len(words)), "D.C.")
        return " ".join(words).upper()
    return " ".join(words)


def generate(count, seen):
    titles = []
    while len(titles) < count:
        title = make_title()
        if not title or title in seen:
            continue
        if "\n" in title or "\r" in title:
            continue
        seen.add(title)
        titles.append(title)
    return titles


def write_pair(titles, inputs_path, expected_path, titlecase):
    expected = []
    for title in titles:
        result = titlecase(title)
        if "\n" in result or "\r" in result:
            raise SystemExit("titlecase() returned more than one line")
        expected.append(result)
    inputs_path.write_text("\n".join(titles) + "\n", encoding="utf-8")
    expected_path.write_text("\n".join(expected) + "\n", encoding="utf-8")


def main():
    random.seed(1)
    # titlecase-go/tests/gen.py -> the python-titlecase repository root
    original = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(original))
    from titlecase import titlecase

    DATA.mkdir(parents=True, exist_ok=True)
    seen = set()
    public = generate(COUNT, seen)
    hidden = generate(COUNT, seen)
    write_pair(public, DATA / "inputs.txt", DATA / "expected.txt", titlecase)
    write_pair(hidden, DATA / "hidden_inputs.txt", DATA / "hidden_expected.txt", titlecase)


if __name__ == "__main__":
    main()
