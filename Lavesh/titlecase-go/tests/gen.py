#!/usr/bin/env python3
"""Generate deterministic titlecase fixtures from the original Python implementation.

Visible titles use random.Random(1). Hidden titles use random.Random(2).
Expected lines are whatever titlecase() returns with default arguments.
"""

import random
import re
import sys
from pathlib import Path


FORBIDDEN = frozenset("\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029")
LINE_COUNT = 2000
# Isolated blanks and pairs only. Runs of three empty lines are rejected.
BLANK_RUNS = (1, 1, 1, 1, 1, 2, 2)

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
ORIGINAL_REPO = HERE.joinpath("..", "..", "python-titlecase").resolve()

NORMAL = (
    "lord", "rings", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
    "apple", "castle", "dragon", "empire", "forest", "garden", "harbor",
    "island", "jungle", "kingdom", "lantern", "mountain", "night", "ocean",
    "palace", "quest", "river", "shadow", "tower", "valley", "winter",
    "yellow", "music", "story", "bridge", "captain", "diamond", "engine",
    "feather", "galaxy", "horizon", "journey", "kettle", "library", "meadow",
    "notebook", "orange", "pebble", "quartz", "rocket", "silver", "thunder",
    "violet", "window", "crystal", "golden", "silent", "ancient", "bright",
    "copper", "distant", "emerald", "frozen", "gentle", "hidden", "iron",
    "kindred", "lunar", "marble", "noble", "pearl", "quiet", "ruby",
    "scarlet", "timber", "urban", "velvet", "wild", "azure", "bold",
    "calm", "deep", "early", "fair", "grand", "happy", "ivory", "jolly",
    "keen", "lucky", "mighty", "north", "open", "proud", "rapid", "solar",
    "true", "upper", "vivid", "warm", "young", "zephyr", "market", "public",
    "report", "summer", "travel", "village", "writer", "chapter", "figure",
    "letter", "moment", "people", "reason", "season", "system", "theory",
    "practice",
)

SMALL = (
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs.",
)

APOS_STEMS = {
    "d": ("artagnan", "angelo", "amico", "este", "oyley", "urso"),
    "o": ("reilly", "brien", "grady", "connor", "neill", "malley", "melveny", "doyle"),
    "l": ("grange", "amour", "oreal", "estrade", "ouverture"),
}

MC_STEMS = (
    "donald", "tavish", "carthy", "gregor", "intosh", "kenzie", "leod",
    "mahon", "namara", "pherson", "cloud", "bride", "clelland", "maier",
    "neustadt", "cay", "do", "foo",
)

HONORIFICS = (
    "Mr", "Mrs", "Ms", "Dr", "MR", "MRS", "MS", "DR", "mr", "mrs", "ms", "dr",
    "mR", "MrS", "mS", "dR", "mRs",
)

INTERNAL = (
    "iTunes", "iPhone", "iPad", "eBay", "macOS", "YouTube", "LinkedIn",
    "JavaScript", "IPv6", "PPPoE", "OmniFocus", "AT&T", "Q&A",
)

CONSONANTS = (
    "cnn", "nth", "html", "css", "php", "sql", "gps", "rgb", "ftp",
    "lcd", "pdf", "xml", "bbc", "nfl", "mlb",
)

Y_WORDS = ("fly", "cry", "myth", "rhythm", "lynx", "gypsy", "sync", "yellow")

DIGITS = (
    "34th", "3rd", "2nd", "1st", "5th", "11th", "12th", "13th",
    "21st", "22nd", "23rd", "100th", "7", "42",
)

ACCENTED = (
    "élan", "über", "naïve", "café", "résumé", "señor", "façade",
    "crème", "brûlée", "niño", "arrivé", "ångström", "piñata", "ýæ", "ñø",
)

# : . ; ? ! - – ‒ — ―
SUBPHRASE = (":", ".", ";", "?", "!", "-", "\u2013", "\u2012", "\u2014", "\u2015")

CANONICAL = (
    "  a  ",
    "\ta\t",
    "   ",
    "\t",
    " \t ",
    "foo  bar",
    "text\twith\ttabs",
    "a  b\tc",
    "  the  lord  of  the  rings  ",
    "the lord of the rings",
    "a an and as at but by en for if in of on or the to v v. via vs vs.",
    "nothing to be afraid of",
    "nothing to be afraid of?",
    "trip via paris",
    "this v that",
    "this v. that",
    "this vs that",
    "this vs. that",
    "done. the start",
    "done: the start",
    "done; the start",
    "done? the start",
    "done! the start",
    "done - the start",
    "done \u2013 the start",
    "done \u2012 the start",
    "done \u2014 the start",
    "done \u2015 the start",
    "Starting Sub-Phrase With a Small Word: a Trick, Perhaps?",
    "Starting a Hyphen Delimited Sub-Phrase With a Small Word - a Trick, Perhaps?",
    "Starting an Em Dash Delimited Sub-Phrase With a Small Word \u2014 a Trick, Perhaps?",
    "my name is o'reilly",
    "O'Reilly should be untouched",
    "l'grange",
    "L'grange",
    "d'artagnan",
    "D'Artagnan",
    "o'reilly's book",
    "d'artagnan's sword",
    "l'grange's farm",
    "o\u2018reilly",
    "l\u2018grange's",
    "mcdonald",
    "MCDonald",
    "mcgregor",
    "McCarthy",
    "mac mc MAC MC machine",
    "mccay-mcbut-mcdo mcdonalds/mcby",
    "mcfoo-bar",
    "foo-mcbar",
    "Mr Smith",
    "MRS SMITH",
    "ms jones",
    "dR who",
    "mR smith",
    "MrS dashwood",
    "Mr mr Mrs Ms Mss Dr dr , Mr. and Mrs. Person",
    "iTunes should be unmolested",
    "ITUNES SHOULD BE UNMOLESTED",
    "iPhone and eBay and macOS",
    "this is just an example.com",
    "this is something listed on del.icio.us",
    "this is http://foo.com",
    "http://a.b/c-d",
    "https://example.com/a-b",
    "a title and/or string",
    "word/word",
    "mother-in-law",
    "end-to-end",
    "a-b end-to-end two-not-three/three-by-four/five-and",
    "words with all consonants like cnn are acronyms",
    "rhythm",
    "nth",
    "fly cry myth",
    "foo bar 5th st",
    "FOO BAR 5TH ST",
    "34th 3rd 2nd",
    "(hello)",
    "(the)",
    '"nothing to be afraid of"',
    "'by the Way, small word at the start but within quotes.'",
    "\u201cYOUNG AND RESTLESS\u201d",
    "\u2018QUOTE\u2019 A GREAT",
    "élan",
    "über",
    "crème brûlée",
    "EL NIÑO A ARRIVÉ HIER",
    "ýæ ñø",
    "ÝÆ ÑØ",
    "THIS IS ALL CAPS AND SHOULD BE ADDRESSED",
    "WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM",
    "Q&A with steve jobs: 'that's what happens in technology'",
    "What is AT&T's problem?",
    "Apple deal with AT&T falls through",
    "reading between the lines of steve jobs\u2019s \u2018thoughts on music\u2019",
    "generalissimo francisco franco: still dead; kieren McCarthy: still a jackass",
    "EPISODE 7 \u2014 THE FORCE AWAKENS",
    "episode 7 \u2013 The force awakens",
    "THE CASE OF X \u2264 7",
    "2lmc Spool: 'gruber on OmniFocus and vapo(u)rware'",
    "A.B",
    "A.B.C.",
    "o'melveny/o'doyle",
    "a mix\u00a0of\tdifferent\u200aspace\u2006characters",
    "Snakes on a Plane \u2014 The TV Edit \u2014 The Famous Line",
    "'QUOTE' A GREAT",
)


def reject_regex_module():
    try:
        import regex  # noqa: F401
    except ImportError:
        return
    raise SystemExit(
        "error: import regex succeeded; answers must come from the re fallback"
    )


def load_titlecase():
    reject_regex_module()
    if not (ORIGINAL_REPO / "titlecase" / "__init__.py").is_file():
        raise SystemExit(
            f"error: original python-titlecase package not found at {ORIGINAL_REPO}"
        )
    sys.path.insert(0, str(ORIGINAL_REPO))
    import titlecase as titlecase_module

    if hasattr(titlecase_module, "REGEX_AVAILABLE") and titlecase_module.REGEX_AVAILABLE:
        raise SystemExit(
            "error: titlecase.REGEX_AVAILABLE is true; answers must come from the re fallback"
        )
    sanity_check(titlecase_module.titlecase)
    return titlecase_module.titlecase


def sanity_check(titlecase):
    probes = (
        ("the lord of the rings", "The Lord of the Rings"),
        ("  a  ", "  a  "),
        ("l'grange", "l'Grange"),
        ("done. the start", "Done. The Start"),
        ("nth", "NTH"),
        ("rhythm", "Rhythm"),
    )
    for source, expected in probes:
        got = titlecase(source)
        if got != expected:
            raise SystemExit(
                "error: original titlecase() did not match a known result for "
                f"{source!r}: got {got!r}"
            )


def require_clean(label, text):
    found = FORBIDDEN.intersection(text)
    if found:
        shown = ", ".join(hex(ord(ch)) for ch in sorted(found))
        raise SystemExit(f"error: {label} contains forbidden character(s): {shown}")


def apply_case(rng, word, style):
    if style == "as_is":
        return word
    if style == "lower":
        return word.lower()
    if style == "upper":
        return word.upper()
    if style == "cap":
        chars = list(word)
        for index, char in enumerate(chars):
            if char.isalpha():
                chars[index] = char.upper()
                for later in range(index + 1, len(chars)):
                    if chars[later].isalpha():
                        chars[later] = chars[later].lower()
                break
        return "".join(chars)
    chars = []
    for char in word:
        if char.isalpha():
            chars.append(char.upper() if rng.random() < 0.5 else char.lower())
        else:
            chars.append(char)
    return "".join(chars)


def join_words(rng, words, allow_double=True, allow_tab=True):
    separators = [" "]
    if allow_double:
        separators.append("  ")
    if allow_tab:
        separators.append("\t")
    pieces = []
    for index, word in enumerate(words):
        if index:
            pieces.append(rng.choice(separators))
        pieces.append(word)
    return "".join(pieces)


def edge(rng):
    alphabet = (" ", " ", "\t")
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 3)))


def normal_words(rng, count):
    return [rng.choice(NORMAL) for _ in range(count)]


def apos_word(rng):
    letter = rng.choice("dol")
    shown = letter.upper() if rng.random() < 0.5 else letter
    mark = "'" if rng.random() < 0.75 else "\u2018"
    stem = apply_case(
        rng,
        rng.choice(APOS_STEMS[letter]),
        rng.choice(("lower", "cap", "upper", "mixed", "as_is")),
    )
    possessive = rng.choice(("", "", "'s", "'s", "'S", "s'", "\u2019s"))
    return shown + mark + stem + possessive


def mc_word(rng):
    prefix = rng.choice(("Mc", "mc", "MC", "Mc", "mc"))
    stem = apply_case(
        rng,
        rng.choice(MC_STEMS),
        rng.choice(("lower", "cap", "upper", "mixed")),
    )
    if len(stem) < 2:
        stem = "donald"
    return prefix + stem


def honorific(rng):
    if rng.random() < 0.7:
        return rng.choice(HONORIFICS)
    base = rng.choice(("mr", "mrs", "ms", "dr"))
    return "".join(char.upper() if rng.random() < 0.5 else char.lower() for char in base)


def internal_word(rng):
    if rng.random() < 0.55:
        return rng.choice(INTERNAL)
    word = rng.choice(NORMAL)
    chars = list(word.lower())
    letters = [index for index, char in enumerate(chars) if char.isalpha()]
    if len(letters) < 2:
        return rng.choice(INTERNAL)
    internal = letters[1:]
    index = rng.choice(internal)
    chars[index] = chars[index].upper()
    if len(internal) > 1 and rng.random() < 0.4:
        other = rng.choice(internal)
        chars[other] = chars[other].upper()
    return "".join(chars)


def domain_word(rng):
    kind = rng.randrange(6)
    if kind == 4:
        return "example.com"
    if kind == 5:
        return "http://a.b/c-d"
    host = rng.choice(("example", "foo", "a", "del", "news", "cdn") + NORMAL[:8])
    tld = rng.choice(("com", "org", "net", "io", "us"))
    if kind == 0:
        return f"{host}.{tld}"
    if kind == 1:
        return f"http://{host}.{tld}"
    if kind == 2:
        left = rng.choice(("a", "b", "cdn"))
        right = rng.choice(("b", "c", "example"))
        path = rng.choice(("c", "path", "x"))
        tail = rng.choice(("d", "e", "y"))
        return f"http://{left}.{right}/{path}-{tail}"
    return f"https://{host}.{tld}/a-b"


def slash_word(rng):
    count = 2 if rng.random() < 0.7 else 3
    pool = SMALL + NORMAL[:24] + ("word", "read", "write")
    return "/".join(rng.choice(pool) for _ in range(count))


def hyphen_word(rng):
    count = rng.choice((2, 3, 3, 4))
    parts = []
    for index in range(count):
        if index % 2 == 1 and rng.random() < 0.75:
            parts.append(rng.choice(("in", "of", "to", "and", "or", "the", "a", "by")))
        else:
            parts.append(rng.choice(NORMAL))
    return "-".join(parts)


def random_token(rng):
    kind = rng.randrange(12)
    if kind == 0:
        return apply_case(rng, rng.choice(NORMAL), rng.choice(("lower", "cap", "upper")))
    if kind == 1:
        return apply_case(rng, rng.choice(SMALL), rng.choice(("lower", "upper", "cap")))
    if kind == 2:
        return apos_word(rng)
    if kind == 3:
        return mc_word(rng)
    if kind == 4:
        return honorific(rng)
    if kind == 5:
        return internal_word(rng)
    if kind == 6:
        return domain_word(rng)
    if kind == 7:
        return slash_word(rng) if rng.random() < 0.5 else hyphen_word(rng)
    if kind == 8:
        return apply_case(rng, rng.choice(CONSONANTS), rng.choice(("lower", "upper")))
    if kind == 9:
        return apply_case(rng, rng.choice(Y_WORDS), rng.choice(("lower", "cap", "upper")))
    if kind == 10:
        return rng.choice(DIGITS)
    return apply_case(rng, rng.choice(ACCENTED), rng.choice(("as_is", "lower", "upper", "cap")))


def build_normal(rng):
    count = rng.randint(3, 12)
    words = normal_words(rng, count)
    if count >= 5 and rng.random() < 0.45:
        words[rng.randint(1, count - 2)] = rng.choice(SMALL)
    style = rng.choice(("lower", "cap", "as_is"))
    return join_words(rng, [apply_case(rng, word, style) for word in words], False, False)


def build_padded(rng):
    words = normal_words(rng, rng.randint(1, 8))
    if rng.random() < 0.6:
        words.insert(rng.randint(0, len(words)), rng.choice(SMALL))
    styled = [
        apply_case(rng, word, rng.choice(("lower", "cap", "upper")))
        for word in words
    ]
    text = join_words(rng, styled, True, True)
    return edge(rng) + text + edge(rng)


def build_small(rng):
    words = [rng.choice(SMALL)]
    middle = rng.randint(2, 6)
    for index in range(middle):
        if index == middle // 2:
            words.append(rng.choice(SMALL))
        words.append(rng.choice(NORMAL))
    words.append(rng.choice(SMALL))
    styled = [
        apply_case(rng, word, rng.choice(("lower", "lower", "upper", "cap", "as_is")))
        for word in words
    ]
    text = join_words(rng, styled, True, True)
    if rng.random() < 0.45:
        text += rng.choice(("?", "!", ".", ",", ":", ";"))
    if rng.random() < 0.35:
        text = edge(rng) + text
    return text


def build_subphrase(rng):
    left = normal_words(rng, rng.randint(2, 6))
    left[-1] = left[-1] + rng.choice(SUBPHRASE)
    small = apply_case(rng, rng.choice(SMALL), rng.choice(("lower", "upper", "cap")))
    right = normal_words(rng, rng.randint(1, 4))
    text = join_words(rng, left, True, False) + " " + small
    if right:
        text += " " + join_words(rng, right, True, False)
    if rng.random() < 0.25:
        text = edge(rng) + text
    if rng.random() < 0.2:
        text = text.upper()
    return text


def build_apostrophe(rng):
    words = normal_words(rng, rng.randint(1, 4))
    words.insert(rng.randint(0, len(words)), apos_word(rng))
    if rng.random() < 0.4:
        words.append(apos_word(rng))
    return join_words(rng, words, True, False)


def build_mc(rng):
    words = [mc_word(rng), rng.choice(NORMAL)]
    if rng.random() < 0.5:
        words.append(mc_word(rng))
    if rng.random() < 0.3:
        words.append(hyphen_word(rng))
    words.insert(0, rng.choice(NORMAL))
    return join_words(rng, words, True, False)


def build_honor(rng):
    name = mc_word(rng) if rng.random() < 0.45 else apply_case(rng, rng.choice(NORMAL), "cap")
    words = [honorific(rng), name]
    words.extend(normal_words(rng, rng.randint(0, 3)))
    if rng.random() < 0.3:
        words.append(honorific(rng))
    text = join_words(rng, words, True, False)
    if rng.random() < 0.2:
        return text.upper()
    return text


def build_internal(rng):
    words = normal_words(rng, rng.randint(2, 6))
    words.insert(rng.randint(0, len(words)), internal_word(rng))
    if rng.random() < 0.4:
        words.append(internal_word(rng))
    return join_words(rng, words, False, False)


def build_all_caps(rng):
    words = normal_words(rng, rng.randint(3, 10))
    words.insert(rng.randint(0, len(words)), rng.choice(SMALL))
    if rng.random() < 0.4:
        words.append(rng.choice(CONSONANTS))
    if rng.random() < 0.3:
        words.append(rng.choice(DIGITS))
    if rng.random() < 0.25:
        words.append(rng.choice(("A.B", "A.", "A.B.C.")))
    return join_words(rng, words, True, True).upper()


def mix_line(rng, text):
    chars = []
    for char in text:
        if char.isalpha():
            chars.append(char.upper() if rng.random() < 0.5 else char.lower())
        else:
            chars.append(char)
    letters = [index for index, char in enumerate(chars) if char.isalpha()]
    if len(letters) < 2:
        return "".join(chars) + " iTunes"
    chars[letters[0]] = chars[letters[0]].lower()
    chars[letters[1]] = chars[letters[1]].upper()
    return "".join(chars)


def build_mixed(rng):
    words = [random_token(rng) for _ in range(rng.randint(3, 8))]
    return mix_line(rng, join_words(rng, words, True, True))


def build_domain(rng):
    words = normal_words(rng, rng.randint(2, 5))
    words.insert(rng.randint(0, len(words)), domain_word(rng))
    if rng.random() < 0.3:
        words.append(rng.choice(SMALL))
    text = join_words(rng, words, True, False)
    if rng.random() < 0.15:
        return text.upper()
    return text


def build_slash_hyphen(rng):
    words = [slash_word(rng) if rng.random() < 0.5 else hyphen_word(rng)]
    words.extend(normal_words(rng, rng.randint(1, 4)))
    words.append(slash_word(rng) if rng.random() < 0.5 else hyphen_word(rng))
    if rng.random() < 0.35:
        words.insert(1, rng.choice(SMALL))
    return join_words(rng, words, True, False)


def build_consonant(rng):
    words = [
        rng.choice(NORMAL),
        rng.choice(CONSONANTS),
        rng.choice(Y_WORDS),
        rng.choice(("cnn", "nth", "rhythm", "fly", "cry", "myth")),
        rng.choice(NORMAL),
    ]
    rng.shuffle(words)
    styled = [
        apply_case(rng, word, rng.choice(("lower", "upper", "cap")))
        for word in words
    ]
    return join_words(rng, styled, True, False)


def build_digits(rng):
    words = [rng.choice(NORMAL)]
    words.extend(rng.choice(DIGITS) for _ in range(rng.randint(1, 3)))
    words.append(rng.choice(("st", "nd", "rd", "street", "avenue", "day")))
    if rng.random() < 0.4:
        words.insert(0, "(" + rng.choice(DIGITS) + ")")
    return join_words(rng, words, True, False)


def build_quotes(rng):
    openers = ("(", "((", "'", '"', "\u201c", "\u2018", "[", "('")
    closers = (")", "))", "'", '"', "\u201d", "\u2019", "]", "')", "")
    inner_word = apply_case(
        rng,
        rng.choice(NORMAL + SMALL + ("hello", "nothing", "élan", "34th")),
        "lower",
    )
    wrapped = rng.choice(openers) + inner_word + rng.choice(closers)
    words = [wrapped, rng.choice(NORMAL), rng.choice(SMALL), rng.choice(NORMAL)]
    if rng.random() < 0.3:
        words.append(rng.choice(openers) + rng.choice(SMALL))
    return join_words(rng, words, True, False)


def build_accent(rng):
    words = [rng.choice(NORMAL), rng.choice(ACCENTED)]
    if rng.random() < 0.6:
        words.append(rng.choice(ACCENTED))
    words.append(rng.choice(SMALL))
    words.append(rng.choice(NORMAL))
    style = rng.choice(("as_is", "lower", "upper", "cap"))
    return join_words(rng, [apply_case(rng, word, style) for word in words], True, False)


def build_combo(rng):
    words = [random_token(rng) for _ in range(rng.randint(4, 9))]
    if rng.random() < 0.8:
        words.insert(rng.randint(0, len(words)), rng.choice(SMALL))
    pieces = [words[0]]
    for word in words[1:]:
        if rng.random() < 0.18:
            pieces[-1] = pieces[-1] + rng.choice(SUBPHRASE)
            if rng.random() < 0.7:
                word = apply_case(rng, rng.choice(SMALL), rng.choice(("lower", "upper")))
            pieces.append(" ")
        else:
            pieces.append(rng.choice((" ", " ", "  ", "\t")))
        pieces.append(word)
    text = "".join(pieces)
    roll = rng.random()
    if roll < 0.12:
        text = text.upper()
    elif roll < 0.28:
        text = mix_line(rng, text)
    if rng.random() < 0.3:
        text = edge(rng) + text + edge(rng)
    return text


BUILDERS = (
    build_normal,
    build_padded,
    build_small,
    build_subphrase,
    build_apostrophe,
    build_mc,
    build_honor,
    build_internal,
    build_all_caps,
    build_mixed,
    build_domain,
    build_slash_hyphen,
    build_consonant,
    build_digits,
    build_quotes,
    build_accent,
    build_combo,
)
WEIGHTS = (20, 8, 8, 8, 6, 5, 5, 5, 6, 6, 5, 6, 5, 4, 5, 4, 14)


def pick_builder(rng):
    roll = rng.randrange(sum(WEIGHTS))
    covered = 0
    for builder, weight in zip(BUILDERS, WEIGHTS):
        covered += weight
        if roll < covered:
            return builder
    return BUILDERS[-1]


def insert_blank_runs(rng, lines, runs):
    run_count = len(runs)
    content_count = len(lines)
    if content_count < run_count - 1:
        raise SystemExit("error: not enough content lines to separate empty lines")
    extras = [0] * (run_count + 1)
    for _ in range(content_count - (run_count - 1)):
        extras[rng.randrange(run_count + 1)] += 1
    output = []
    index = 0

    def take(count):
        nonlocal index
        chunk = lines[index:index + count]
        if len(chunk) != count:
            raise SystemExit("error: blank insertion ran out of content lines")
        index += count
        return chunk

    output.extend(take(extras[0]))
    for position, run in enumerate(runs):
        if run < 1 or run > 2:
            raise SystemExit("error: empty-line run must be 1 or 2")
        output.extend([""] * run)
        if position < run_count - 1:
            output.extend(take(1 + extras[position + 1]))
        else:
            output.extend(take(extras[run_count]))
    if index != content_count:
        raise SystemExit("error: blank insertion did not consume every content line")
    return output


def generate(rng):
    runs = list(BLANK_RUNS)
    rng.shuffle(runs)
    content_count = LINE_COUNT - sum(runs)
    if len(CANONICAL) >= content_count:
        raise SystemExit("error: canonical examples do not fit in the content budget")
    for example in CANONICAL:
        require_clean("canonical title", example)
    lines = list(CANONICAL)
    while len(lines) < content_count:
        line = pick_builder(rng)(rng)
        require_clean("generated title", line)
        if line == "":
            raise SystemExit("error: a builder returned an empty title")
        lines.append(line)
    if len(lines) != content_count:
        raise SystemExit("error: content line count drifted")
    rng.shuffle(lines)
    lines = insert_blank_runs(rng, lines, runs)
    if len(lines) != LINE_COUNT:
        raise SystemExit(f"error: generated {len(lines)} lines, expected {LINE_COUNT}")
    validate_lines(lines, "generated set")
    return lines


def validate_lines(lines, label):
    if len(lines) != LINE_COUNT:
        raise SystemExit(f"error: {label} has {len(lines)} lines, expected {LINE_COUNT}")
    empties = 0
    run = 0
    max_run = 0
    saw_pair = False
    for index, line in enumerate(lines):
        require_clean(f"{label} line {index + 1}", line)
        if line == "":
            empties += 1
            run += 1
            max_run = max(max_run, run)
            if run == 2:
                saw_pair = True
            if run > 2:
                raise SystemExit(f"error: {label} has an empty-line run longer than 2")
        else:
            run = 0
    if empties < 3:
        raise SystemExit(f"error: {label} needs a few empty lines")
    if max_run > 2 or not saw_pair:
        raise SystemExit(f"error: {label} empty-line runs were not 1 or 2")
    assert_features(lines, label)


def has_word(lines, word):
    pattern = re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)
    return any(pattern.search(line) for line in lines)


def assert_features(lines, label):
    def need(description, predicate):
        if not predicate:
            raise SystemExit(f"error: {label} is missing {description}")

    blob = "\n".join(lines)
    need("the padded line '  a  '", any(line == "  a  " for line in lines))
    need("a tab", any("\t" in line for line in lines))
    need("a double space", any("  " in line for line in lines))
    need(
        "leading and trailing whitespace",
        any(
            line[:1] in (" ", "\t") and line[-1:] in (" ", "\t") and line.strip() != ""
            for line in lines
        ),
    )
    for word in (
        "a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on",
        "or", "the", "to", "via", "vs", "v.",
    ):
        need(f"small word {word}", has_word(lines, word))
    folded = blob.lower().replace("\u2018", "'")
    for snippet in (
        "o'reilly", "d'artagnan", "l'grange",
        "o'reilly's", "d'artagnan's", "l'grange's",
    ):
        need(snippet, snippet in folded)
    need("an Mc name", re.search(r"(?<![A-Za-z])Mc[A-Za-z]{2,}", blob) is not None)
    need("an mc name", re.search(r"(?<![A-Za-z])mc[A-Za-z]{2,}", blob) is not None)
    need("an MC name", re.search(r"(?<![A-Za-z])MC[A-Za-z]{2,}", blob) is not None)
    for word in ("Mr", "MRS", "ms", "dR", "mR"):
        need(f"honorific {word}", has_word(lines, word))
    need("iTunes", "iTunes" in blob)
    need("an all-caps line", any(line.upper() == line and any(ch.isalpha() for ch in line) for line in lines))
    need(
        "a mixed-case line",
        any(any(ch.islower() for ch in line) and any(ch.isupper() for ch in line) for line in lines),
    )
    need("example.com", "example.com" in blob)
    need("http://a.b/c-d", "http://a.b/c-d" in blob)
    need("and/or", "and/or" in blob)
    need("a hyphenated word", re.search(r"\w-\w", blob) is not None)
    for word in ("cnn", "nth", "rhythm", "fly", "cry", "myth", "34th", "3rd"):
        need(word, has_word(lines, word))
    need("a leading parenthesis", any(line.startswith("(") for line in lines))
    need(
        "a leading quote",
        any(line[:1] in ("'", '"', "\u201c", "\u2018") for line in lines),
    )
    need("élan", "élan" in blob.lower())
    need("über", "über" in blob.lower())


def expected_lines(titlecase, lines):
    output = []
    for index, line in enumerate(lines):
        result = titlecase(line)
        if not isinstance(result, str):
            raise SystemExit(f"error: titlecase() returned {type(result).__name__}")
        require_clean(f"expected line {index + 1}", result)
        if len(result.split("\n")) != 1:
            raise SystemExit(
                f"error: titlecase() introduced a line break for {line!r}"
            )
        output.append(result)
    if len(output) != len(lines):
        raise SystemExit("error: expected line count does not match input")
    return output


def write_lines(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for line in lines:
            require_clean(path.name, line)
            handle.write(line)
            handle.write("\n")


def read_lines(path):
    with path.open("r", encoding="utf-8", newline="\n") as handle:
        data = handle.read()
    if "\r" in data:
        raise SystemExit(f"error: {path} contains a carriage return")
    if not data.endswith("\n"):
        raise SystemExit(f"error: {path} does not end with a newline")
    parts = data.split("\n")
    if parts[-1] != "":
        raise SystemExit(f"error: {path} is missing its final newline")
    lines = parts[:-1]
    for index, line in enumerate(lines):
        require_clean(f"{path.name} line {index + 1}", line)
    return lines


def write_pair(titlecase, inputs, inputs_path, expected_path):
    expected = expected_lines(titlecase, inputs)
    write_lines(inputs_path, inputs)
    write_lines(expected_path, expected)
    read_inputs = read_lines(inputs_path)
    read_expected = read_lines(expected_path)
    if read_inputs != inputs or read_expected != expected:
        raise SystemExit(f"error: {inputs_path.name} did not round-trip as UTF-8")
    if len(read_inputs) != len(read_expected):
        raise SystemExit(
            f"error: {inputs_path.name} and {expected_path.name} differ in length"
        )
    for index, (source, want) in enumerate(zip(read_inputs, read_expected)):
        if titlecase(source) != want:
            raise SystemExit(
                f"error: {expected_path.name} line {index + 1} "
                "does not match titlecase()"
            )


def main():
    titlecase = load_titlecase()
    visible = generate(random.Random(1))
    hidden = generate(random.Random(2))
    if visible == hidden:
        raise SystemExit("error: visible and hidden sets are identical")
    write_pair(titlecase, visible, DATA_DIR / "inputs.txt", DATA_DIR / "expected.txt")
    write_pair(
        titlecase,
        hidden,
        DATA_DIR / "hidden_inputs.txt",
        DATA_DIR / "hidden_expected.txt",
    )
    visible_blanks = sum(line == "" for line in visible)
    hidden_blanks = sum(line == "" for line in hidden)
    print(
        f"wrote {LINE_COUNT} visible titles ({visible_blanks} empty) and "
        f"{LINE_COUNT} hidden titles ({hidden_blanks} empty)"
    )


if __name__ == "__main__":
    main()
