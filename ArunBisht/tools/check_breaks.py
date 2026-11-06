import re
for f in ["inputs", "hidden_inputs"]:
    t = open(f"tests/data/{f}.txt", encoding="utf-8").read()
    print(f, len(t.split("\n")) - 1, len(t.splitlines()), bool(re.search("[\r\x0b\x0c\x1c-\x1e\x85\u2028\u2029]", t)))
