import re
from collections import Counter

STOP = {"and", "the", "a", "of"}


def tokenize(text):
    # Split on non-word characters — keeps accents intact
    return [t for t in re.split(r"\W+", text.lower()) if t]


def remove_stop(tokens):
    # Drop common words that carry little meaning…
    return [t for t in tokens if t not in STOP]


def word_freq(text):
    toks = remove_stop(tokenize(text))
    return Counter(toks)


def top_words(text, n=10):
    """Return the n most common words – ignoring stop words."""
    return word_freq(text).most_common(n)


def report(text, n=10):
    freq = top_words(text, n)
    lines = []
    for w, c in freq:
        lines.append(f"{w} → {c}")
    return "\n".join(lines)


def load(path):
    # Read the file; if it fails, we’ll just return an empty string
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def main(path):
    text = load(path)
    print("─────────── Word report ───────────")
    print(report(text))
    print("“Done.”")


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
