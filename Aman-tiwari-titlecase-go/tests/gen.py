"""Generate test inputs and freeze the expected answers.

Run by the task author only (never by the verifier):

    python3 -I tests/gen.py [path-to-python-titlecase]

- random.seed(1) -> the same files every run
- 2000 visible titles  -> data/inputs.txt        + data/expected.txt
- 2000 hidden titles   -> data/hidden_inputs.txt + data/hidden_expected.txt
- Expected answers come ONLY from running the ORIGINAL Python titlecase().
"""

import random
import sys
from pathlib import Path

N_VISIBLE = 2000
N_HIDDEN = 2000

# ---------------------------------------------------------------- word pools
NORMAL = """
lord rings war peace star wars hope river city night day light dark house
garden story world music road home water fire stone heart dream king queen
north south winter summer secret life death time love song game book letter
history science mountain ocean island empire machine shadow ghost return
journey tale guide future past art street market child mother father friend
""".split()

SMALL = ["a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
         "of", "on", "or", "the", "to", "v", "v.", "via", "vs", "vs."]

MIXED_CASE = ["iPhone", "eBay", "JavaScript", "macOS", "YouTube", "NASA", "FBI",
              "PhD", "McDonald's", "iOS", "GitHub", "LaTeX", "OpenAI", "pH",
              "AT&T", "Q&A", "iTunes", "R&D"]

INLINE_PERIOD = ["example.com", "U.S.", "e.g.", "i.e.", "node.js", "a.b.c",
                 "U.K.", "www.site.org", "J.R.R.", "v1.2", "Ph.D."]

URLS = ["http://example.com/path", "https://www.example.org/a/b",
        "ftp://files.net/x", "http://a.co", "//cdn.site/x"]

APOSTROPHE = ["o'neil", "d'angelo", "l'oreal", "o‘brien", "don't", "it's",
              "rock'n'roll", "d'artagnan", "O'NEIL", "l'amour", "o'clock",
              "D'arcy", "m'lady", "y'all"]

MC_WORDS = ["mcdonald", "mcintosh", "MCDONALD", "mcfly", "mc", "Mcx",
            "macbeth", "macbook", "mcqueen", "MCQUEEN", "mc-hammer"]

TITLES = ["mr", "mrs", "ms", "dr", "MR", "Dr.", "mrs.", "MS", "dR", "mrS"]

SLASH = ["input/output", "and/or", "a/b/c", "km/h", "24/7", "on/off",
         "one/two//three", "/root", "end/"]

HYPHEN = ["well-known", "x-ray", "self-made", "state-of-the-art", "-leading",
          "trailing-", "up-to-date", "e-mail", "a-z", "t-shirt", "co-op",
          "mother-in-law", "the-end"]

CONSONANTS = ["bbc", "nhs", "psst", "hmm", "st", "tv", "cdc", "rhythm", "crwth",
              "brr", "nth", "ms", "dvd", "html", "sql", "xml", "pdf", "tsk"]

UNICODE = ["café", "über", "köln", "naïve", "señor", "garçon", "straße",
           "ÉCOLE", "ÜBER", "ñandú", "éclair", "øre", "ångström", "çà",
           "œuvre", "ΑΘΗΝΑ", "αθήνα", "москва", "МОСКВА"]

NUMBERS = ["2nd", "1990s", "3d", "4x4", "100%", "mp3", "b2b", "7", "42nd",
           "x2", "r2-d2", "c3po", "50/50", "34th", "3rd", "1st", "5th", "10th",
           "21st", "101st"]

# The checked examples from NOTES.md, used as whole titles (sometimes with
# extra words around them).
NOTES_EXAMPLES = [
    "the lord of the rings", '"the quoted title"', "smith vs jones",
    "smith v. jones", "a tale of two cities", "...and then",
    "what are you looking at", "what is it for?", "star wars: a new hope",
    "end. the next", "war - the sequel", "the iPhone and eBay",
    "the NASA mission", "visit example.com today", "a guide to U.S. policy",
    "NASA LAUNCHES A ROCKET", "ÉCOLE NORMALE", "THE U.S. ARMY",
    "o'neil and d'angelo", "l'oreal paris", "mcdonald and macbeth",
    "macbook pro", "MC hammer", "mr smith and dr jones", "dr. who",
    "input/output errors", "one/two//three", "see http://example.com/path",
    "a well-known fact", "in-the-middle", "an ode to x-ray",
    "the bbc and the nhs", "psst and hmm", "st louis and the cdc",
    "hello   world\tagain", "über alles in köln", "café au lait",
]

WRAP = [("\"", "\""), ("'", "'"), ("“", "”"), ("‘", "’"),
        ("(", ")"), ("[", "]"), ("...", ""), ("", "?"), ("", "!"),
        ("", ":"), ("", "."), ("", "..."), ("", ","), ("*", "*"), ("_", "_")]

SEPARATORS = [": ", ". ", "; ", "? ", "! ", " - ", " – ", " — ",
              " ‒ ", " ― ", ", ", " / "]

SPACES = [" "] * 30 + ["  ", "\t", " ", "   ", " \t", " "]

POOLS = [
    (NORMAL, 30), (SMALL, 25), (MIXED_CASE, 5), (INLINE_PERIOD, 4),
    (URLS, 2), (APOSTROPHE, 5), (MC_WORDS, 4), (TITLES, 4), (SLASH, 4),
    (HYPHEN, 5), (CONSONANTS, 5), (UNICODE, 5), (NUMBERS, 3),
]


def pick_word(rng: random.Random) -> str:
    pool = rng.choices([p for p, _ in POOLS], weights=[w for _, w in POOLS])[0]
    word = rng.choice(pool)
    r = rng.random()
    if r < 0.10:
        word = word.upper()
    elif r < 0.20:
        word = word.capitalize()
    elif r < 0.23:
        word = word.swapcase()
    if rng.random() < 0.08:
        left, right = rng.choice(WRAP)
        word = left + word + right
    return word


def notes_title(rng: random.Random) -> str:
    example = rng.choice(NOTES_EXAMPLES)
    side = rng.randrange(4)
    if side == 1:
        example = pick_word(rng) + rng.choice(SPACES) + example
    elif side == 2:
        example = example + rng.choice(SPACES) + pick_word(rng)
    elif side == 3:
        example = example.upper()
    return example


def make_title(rng: random.Random) -> str:
    if rng.random() < 0.06:
        return notes_title(rng)
    n = rng.randint(1, 9)
    parts = []
    for i in range(n):
        if i and rng.random() < 0.12:
            parts.append(rng.choice(SEPARATORS))
        elif i:
            parts.append(rng.choice(SPACES))
        parts.append(pick_word(rng))
    title = "".join(parts)
    r = rng.random()
    if r < 0.12:
        title = title.upper()          # all-caps line
    elif r < 0.15:
        title = " " + title            # leading space
    elif r < 0.18:
        title = title + " "            # trailing space
    # One title per line: never allow line breaks inside a title.
    for bad in ("\r", "\n", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85",
                " ", " "):
        assert bad not in title
    return title


def make_set(rng: random.Random, n: int, avoid: set[str]) -> list[str]:
    out: list[str] = []
    seen = set(avoid)
    while len(out) < n:
        t = make_title(rng)
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def write_lines(path: Path, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        for line in lines:
            f.write(line + "\n")


def main() -> None:
    here = Path(__file__).resolve().parent
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parents[1] / "python-titlecase"
    sys.dont_write_bytecode = True  # keep the original repo untouched
    sys.path.insert(0, str(repo))
    import titlecase as tc

    # Ground truth = plain install (built-in `re`), default arguments.
    assert tc.REGEX_AVAILABLE is False, "uninstall the optional `regex` package first"
    assert tc.__version__ == "2.4.1", tc.__version__

    random.seed(1)
    rng = random  # the seeded global generator
    visible = make_set(rng, N_VISIBLE, set())
    hidden = make_set(rng, N_HIDDEN, set(visible))

    data = here / "data"
    data.mkdir(exist_ok=True)
    for name, inputs in (("", visible), ("hidden_", hidden)):
        expected = [tc.titlecase(t) for t in inputs]
        for e in expected:
            assert "\n" not in e and "\r" not in e
        write_lines(data / f"{name}inputs.txt", inputs)
        write_lines(data / f"{name}expected.txt", expected)
    print(f"wrote {len(visible)} visible + {len(hidden)} hidden titles to {data}")


if __name__ == "__main__":
    main()
