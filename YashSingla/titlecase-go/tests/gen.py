"""Generate deterministic titlecase input and oracle-output datasets."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random

random.seed(1)
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "environment" / "python-titlecase" / "titlecase" / "__init__.py"
SPEC = spec_from_file_location("bundled_python_titlecase", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load bundled titlecase source: {SOURCE}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

tokens = [
    "river", "garden", "quiet", "bright", "silver", "morning", "window",
    "journey", "story", "paper", "blue", "mountain", "clock", "summer",
    "dream", "small", "city", "music", "shadow", "open", "world", "light",
    "a", "an", "and", "as", "at", "but", "by", "en", "for", "if", "in",
    "of", "on", "or", "the", "to", "via", "vs", "v",
]

def ordinary():
    count = random.randint(2, 7)
    return " ".join(random.choice(tokens) for _ in range(count))

def make_title():
    kind = random.randrange(16)
    base = ordinary()
    if kind == 0:
        return base.upper()
    if kind == 1:
        return random.choice(["o'", "d'", "l'", "O’", "D’", "L’"]) + random.choice(["neill", "angelo", "artagnan", "ivry"])
    if kind == 2:
        return random.choice(["mc", "Mc", "MC"]) + random.choice(["donald", "intyre", "queen", "kay"])
    if kind == 3:
        return random.choice(["mr", "mrs", "ms", "dr", "MR", "Dr"]) + " " + base
    if kind == 4:
        return random.choice(["J. R. R. Tolkien", "A.B. Smith", "U.S.A. history", "eBay", "iPhone", "NASA report"])
    if kind == 5:
        return random.choice(["war/peace", "north/south", "a/b/c", "http://example.com/path"])
    if kind == 6:
        return random.choice(["state-of-the-art", "mother-in-law", "long-term plan", "rock-and-roll"])
    if kind == 7:
        return random.choice(["one: the sequel", "quiet; and then", "hello? a return", "wait! the end", "day. in the sun"])
    if kind == 8:
        return random.choice(["(hello) and goodbye", '"a brave new world"', "[the last garden]", "#bright morning"])
    if kind == 9:
        return random.choice(["HTML and XML guide", "BBC news in the USA", "XYZ river", "QRS and ABC"])
    if kind == 10:
        return random.choice(["  ".join([base, ordinary()]), "\t".join([base, ordinary()]), base + "  "])
    if kind == 11:
        return random.choice(["a tale of two cities", "the lord of the rings", "war and peace", "a day in the life"])
    if kind == 12:
        return random.choice(["rock - and - roll", "a - the answer", "one—two and three"])
    if kind == 13:
        return random.choice(["McDONALD meets eBay", "d'ARTAGNAN and the king", "DR. SMITH vs. JONES"])
    if kind == 14:
        return random.choice(["river: of dreams", "city—of glass", "paper? the answer", "music! and light"])
    return base.title()

def generate(count, excluded):
    found = set()
    while len(found) < count:
        title = make_title()
        if "\n" not in title and "\r" not in title and title not in excluded:
            found.add(title)
    return sorted(found)

normal = generate(2000, set())
hidden = generate(2000, set(normal))

data = ROOT / "tests" / "data"
data.mkdir(parents=True, exist_ok=True)
for name, titles in (("inputs.txt", normal), ("hidden_inputs.txt", hidden)):
    (data / name).write_text("".join(title + "\n" for title in titles), encoding="utf-8", newline="\n")
for input_name, output_name in (("inputs.txt", "expected.txt"), ("hidden_inputs.txt", "hidden_expected.txt")):
    titles = (data / input_name).read_text(encoding="utf-8").splitlines()
    results = [MODULE.titlecase(title) for title in titles]
    if any("\n" in result or "\r" in result for result in results):
        raise RuntimeError(f"Oracle produced a multiline result for {input_name}")
    (data / output_name).write_text("".join(result + "\n" for result in results), encoding="utf-8", newline="\n")
