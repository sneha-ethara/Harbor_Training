"""Generate titlecase fixtures from the original Python implementation.

Inputs mix ordinary words with the rules and the example titles in NOTES.md.
Expected files are produced only by calling that original titlecase().
"""

import random
import string
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
COUNT = 2000

# Rule list, with the example inputs from NOTES.md. Outputs are not stored.
NOTES_CASES = [
    (
        "Runs of line breaks collapse, so a blank line is dropped by default",
        "Line number one",
    ),
    (
        "Runs of line breaks collapse, so a blank line is dropped by default",
        "and Line three",
    ),
    (
        "Original space characters between words are preserved",
        "text\twith\ttabs",
    ),
    (
        "A callback result would be kept, but the default function title-cases the word",
        "at&t",
    ),
    (
        "On an all-uppercase line, a run of initials is left as written",
        "A.B. MEETING",
    ),
    (
        "d' / o' / l' words: d and l stay lower, o is capitalized, next letter is capitalized",
        "l'grange",
    ),
    (
        "Mc / mc / MC prefix is capitalized and the remainder is title-cased",
        "oblon, spivak, mcclelland, maier & neustadt",
    ),
    (
        "Mr, Mrs, Ms, and Dr keep their spelling with the first letter uppercase",
        "Mr McTavish went to MacDonalds",
    ),
    (
        "A word with a period between two letters is left unchanged",
        "this is just an example.com",
    ),
    (
        "An existing capital later in a word is left unchanged when the line is not all uppercase",
        "iTunes should be unmolested",
    ),
    (
        "Small words stay lowercase: a an and as at but by en for if in of on or the to v v. via vs vs.",
        "this vs that",
    ),
    (
        "A slash splits a word; a double slash does not",
        "word/word",
    ),
    (
        "A hyphen splits a word, and the pieces skip the first-word and last-word small-word fix",
        "a-b end-to-end two-not-three/three-by-four/five-and",
    ),
    (
        "On an all-uppercase line, a word not kept by an earlier rule is lowercased first",
        "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    ),
    (
        "A consonant-only word longer than two letters is uppercased; y counts as a vowel",
        "Words with all consonants like cnn are acronyms",
    ),
    (
        "Any other word has its first letter capitalized; digits and ordinals stay put",
        "34th 3rd 2nd",
    ),
    (
        "A small word at the start of the line is capitalized",
        "a thing",
    ),
    (
        "A small word at the end of the line is capitalized, including one trailing punctuation mark",
        "Small word at end is nothing to be afraid of",
    ),
    (
        "A small word after sub-phrase punctuation and a space is capitalized",
        "Starting Sub-Phrase With a Small Word: a Trick, Perhaps?",
    ),
]

VERBATIM = [text for _rule, text in NOTES_CASES]

WORDS = [
    "apple", "banana", "castle", "river", "market", "silver", "golden", "winter",
    "summer", "bridge", "garden", "harbor", "captain", "letter", "window", "forest",
    "mountain", "valley", "ocean", "planet", "story", "music", "light", "shadow",
    "paper", "stone", "cloud", "storm", "field", "road", "house", "school", "friend",
    "family", "secret", "public", "private", "simple", "quick", "brown", "jumps",
    "night", "morning", "evening", "coffee", "water", "bread", "table", "chair",
    "book", "phone", "camera", "travel", "city", "village", "kingdom", "queen",
    "prince", "soldier", "artist", "writer", "science", "history", "future",
    "memory", "dream", "voice", "color", "shape", "number", "system", "method",
    "result", "question", "answer", "problem", "reason", "moment", "season",
    "holiday", "office", "station", "airport", "island", "desert", "jungle",
    "prairie", "candle", "mirror", "pocket", "engine", "signal", "library",
]

SMALL = [
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in", "of",
    "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
]

SUBPHRASE_PUNCT = [":", ".", ";", "?", "!", "-", "\u2013", "\u2012", "\u2014", "\u2015"]
ODD_SPACES = [" ", "\t", "\u00a0", "\u200a", "\u2006"]
CONSONANTS = "bcdfghjklmnpqrstvwxz"


def words(count):
    return [random.choice(WORDS) for _ in range(count)]


def surround(fragment):
    left = words(random.randint(0, 3))
    right = words(random.randint(0, 3))
    parts = [part for part in (" ".join(left), fragment, " ".join(right)) if part]
    return " ".join(parts)


def case_normal():
    pieces = []
    for _ in range(random.randint(2, 9)):
        if random.random() < 0.25:
            pieces.append(random.choice(SMALL))
            continue
        word = random.choice(WORDS)
        pieces.append(random.choice((word, word.capitalize(), word.upper())))
    return " ".join(pieces)


def case_small_edges():
    kind = random.choice(("start", "end", "both"))
    middle = " ".join(words(random.randint(1, 5)))
    if kind == "start":
        punct = random.choice(("", "'", "\u2018", '"', "\u201c"))
        return punct + random.choice(SMALL) + " " + middle
    if kind == "end":
        trail = random.choice(("", "?", "!", ".", ","))
        return middle + " " + random.choice(SMALL) + trail
    return random.choice(SMALL) + " " + middle + " " + random.choice(SMALL)


def case_subphrase():
    left = " ".join(words(random.randint(2, 5)))
    small = random.choice(("a", "an", "the", "of", "and", "or", "to", "in"))
    right = " ".join(words(random.randint(1, 4)))
    return left + random.choice(SUBPHRASE_PUNCT) + " " + small + " " + right


def case_all_caps():
    pieces = [word.upper() for word in words(random.randint(3, 8))]
    if random.random() < 0.7 and len(pieces) > 2:
        pieces.insert(random.randint(1, len(pieces) - 1), random.choice(("AND", "THE", "OF", "OR", "TO", "VS")))
    return " ".join(pieces)


def case_initials():
    letters = [random.choice(string.ascii_uppercase) for _ in range(random.randint(2, 4))]
    initials = ".".join(letters) + random.choice(("", "."))
    pieces = [word.upper() for word in words(random.randint(2, 5))]
    pieces.insert(random.randint(0, len(pieces)), initials)
    return " ".join(pieces)


def case_apostrophe():
    letter = random.choice("dolDOL")
    rest = random.choice(WORDS)
    token = letter + random.choice(("'", "\u2018")) + rest
    if random.random() < 0.4:
        token += "'s"
    return surround(token)


def case_mc():
    prefix = random.choice(("Mc", "mc", "MC"))
    return surround(prefix + random.choice(WORDS))


def case_honorific():
    honorific = random.choice(("mr", "mrs", "ms", "dr", "Mr", "MRS", "Ms", "DR", "Dr"))
    return surround(honorific)


def case_internal_period():
    host = random.choice(WORDS)
    tld = random.choice(("com", "org", "us", "io"))
    return surround(host + "." + tld)


def case_internal_caps():
    word = random.choice(WORDS)
    camel = word[0].lower() + word[1].upper() + word[2:]
    ampersand = random.choice(WORDS).upper()[:2] + "&" + random.choice(string.ascii_uppercase)
    token = random.choice((camel, ampersand, "iTunes", "AT&T"))
    return surround(token)


def case_slash():
    parts = []
    for _ in range(random.randint(2, 3)):
        parts.append(random.choice(SMALL) if random.random() < 0.5 else random.choice(WORDS))
    return surround("/".join(parts))


def case_url():
    host = random.choice(WORDS)
    tld = random.choice(("com", "org"))
    return surround("http://" + host + "." + tld)


def case_hyphen():
    parts = []
    for _ in range(random.randint(2, 4)):
        parts.append(random.choice(SMALL) if random.random() < 0.5 else random.choice(WORDS))
    return surround("-".join(parts))


def case_acronym():
    length = random.randint(3, 5)
    acronym = "".join(random.choice(CONSONANTS) for _ in range(length))
    casing = random.choice((str.lower, str.upper, str.capitalize))
    return surround(casing(acronym))


def case_ordinal():
    ordinals = []
    for _ in range(random.randint(1, 3)):
        ordinals.append(str(random.randint(1, 40)) + random.choice(("st", "nd", "rd", "th")))
    return surround(" ".join(ordinals))


def case_vs():
    small = random.choice(("v", "v.", "vs", "vs.", "via"))
    return random.choice(WORDS) + " " + small + " " + random.choice(WORDS)


def case_spaces():
    return random.choice(ODD_SPACES).join(words(random.randint(3, 6)))


def case_mixed():
    pieces = words(random.randint(2, 4))
    tricky = random.choice((
        "".join(random.choice(CONSONANTS) for _ in range(random.randint(3, 4))),
        random.choice(("mc", "Mc", "MC")) + random.choice(WORDS),
        random.choice(WORDS) + "/" + random.choice(WORDS),
        random.choice(WORDS) + "-" + random.choice(SMALL) + "-" + random.choice(WORDS),
        random.choice(WORDS) + ".com",
        random.choice(("mr", "mrs", "ms", "dr")),
        random.choice(("v", "vs", "via", "v.", "vs.")),
    ))
    pieces.insert(random.randint(0, len(pieces)), tricky)
    return " ".join(pieces)


GENERATORS = [
    case_normal,
    case_small_edges,
    case_subphrase,
    case_all_caps,
    case_initials,
    case_apostrophe,
    case_mc,
    case_honorific,
    case_internal_period,
    case_internal_caps,
    case_slash,
    case_url,
    case_hyphen,
    case_acronym,
    case_ordinal,
    case_vs,
    case_spaces,
    case_mixed,
]


def build():
    lines = [random.choice(GENERATORS)() for _ in range(COUNT)]
    for pos, example in zip(random.sample(range(COUNT), len(VERBATIM)), VERBATIM):
        lines[pos] = example
    return lines


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for line in lines:
            if "\n" in line or "\r" in line:
                raise SystemExit("refusing to write a broken line: %r" % (line,))
            handle.write(line + "\n")


def expected_for(lines):
    original = (Path(__file__).resolve().parents[1] / ".." / "python-titlecase").resolve()
    sys.path.insert(0, str(original))
    from titlecase import titlecase

    results = []
    for line in lines:
        result = titlecase(line)
        if "\n" in result or "\r" in result:
            raise SystemExit("titlecase() returned a line break for %r" % (line,))
        results.append(result)
    return results


def main():
    random.seed(1)
    public = build()
    hidden = build()
    if public == hidden:
        raise SystemExit("hidden inputs matched the public inputs")
    if len(public) != COUNT or len(hidden) != COUNT:
        raise SystemExit("expected %s titles in each file" % COUNT)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_lines(DATA_DIR / "inputs.txt", public)
    write_lines(DATA_DIR / "hidden_inputs.txt", hidden)
    write_lines(DATA_DIR / "expected.txt", expected_for(public))
    write_lines(DATA_DIR / "hidden_expected.txt", expected_for(hidden))


if __name__ == "__main__":
    main()
