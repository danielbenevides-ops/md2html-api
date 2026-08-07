"""Extra billable API utility endpoints for the MD2HTML product.

Three pure-stdlib handlers designed to plug into server.py's existing
http.server routing. Each is a callable `handler(body: str) -> str` so
it can be wired in with a one-line dispatch entry.

Endpoints:
    /json/prettify  - Pretty-print compact/ugly JSON.
    /text/stats     - Word/char counts, reading time, top words.
    /slug           - Turn an arbitrary title into a URL-safe slug.

All functions use only the Python standard library.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from typing import Dict, Any, Callable


def json_prettify(body: str) -> str:
    """Pretty-print a compact or minified JSON string.

    Args:
        body: Raw JSON text (may be compact/ugly).

    Returns:
        Indented, 2-space pretty-printed JSON.

    Raises:
        ValueError: If the input is not valid JSON.
    """
    try:
        return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc


def text_stats(body: str) -> str:
    """Compute statistics for a block of text.

    Returns a JSON string with:
        - words: total whitespace-separated tokens
        - chars: total characters (incl. whitespace)
        - chars_no_spaces: character count excluding whitespace
        - reading_time_min: estimated minutes at 200 wpm (float)
        - top_words: list of [word, count] for top 5 (case-folded, alpha-only)

    Args:
        body: Arbitrary text.

    Returns:
        JSON string with the stats object.
    """
    words = body.split()
    word_count = len(words)
    char_count = len(body)
    chars_no_spaces = len(re.sub(r"\s+", "", body))
    reading_time = round(word_count / 200, 2) if word_count else 0.0

    # Case-fold, keep only alphabetic tokens, length > 1.
    alpha_words = re.findall(r"[A-Za-z]+", body.lower())
    top = Counter(alpha_words).most_common(5)

    stats: Dict[str, Any] = {
        "words": word_count,
        "chars": char_count,
        "chars_no_spaces": chars_no_spaces,
        "reading_time_min": reading_time,
        "top_words": [[w, c] for w, c in top],
    }
    return json.dumps(stats, ensure_ascii=False)


def slugify(body: str) -> str:
    """Convert a title string into a URL-safe slug.

    Normalization steps: Unicode NFKD decomposition, strip non-ASCII,
    lowercase, replace non-alphanumeric runs with single hyphens,
    trim leading/trailing hyphens.

    Args:
        body: Title or heading text.

    Returns:
        URL-safe slug, e.g. "hello-world".

    Examples:
        "Hello, World!"          -> "hello-world"
        "Café — Menus & Drinks"  -> "cafe-menus-drinks"
        "  Über  10x  Cool!  "   -> "uber-10x-cool"
    """
    # Decompose accents, drop combining marks, keep ASCII.
    normalized = unicodedata.normalize("NFKD", body)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    # Replace any run of non-alphanumeric chars with one hyphen.
    hyphenated = re.sub(r"[^a-z0-9]+", "-", lowered)
    return hyphenated.strip("-")


# -- Dispatch map for easy server.py integration ---------------------------
# In server.py, route by path -> call HANDLERS[path](body).decode() and
# return as the HTTP response body. Each returns a str (JSON or slug).
HANDLERS: Dict[str, Callable[[str], str]] = {
    "/json/prettify": json_prettify,
    "/text/stats": text_stats,
    "/slug": slugify,
}


def _test() -> None:
    """Run lightweight self-tests; print PASS/FAIL for each endpoint."""

    # 1. /json/prettify
    ugly = '{"b":2,"a":1,"nested":{"x":[1,2]}}'
    pretty = json_prettify(ugly)
    assert "\n" in pretty and '"a": 1' in pretty, "prettify failed"
    # Round-trip equivalence.
    assert json.loads(pretty) == json.loads(ugly), "prettify changed data"
    print("PASS /json/prettify")

    # 2. /text/stats
    sample = "The quick brown fox. The fox jumps over the lazy dog!"
    expected_words = len(sample.split())  # 11 tokens ("fox." counted by split)
    out = json.loads(text_stats(sample))
    assert out["words"] == expected_words, f"word count: {out['words']}"
    assert out["chars"] == len(sample), "char mismatch"
    assert out["reading_time_min"] == round(expected_words / 200, 2), "reading time"
    # "the" appears 3 times (The, The, the), "fox" twice.
    count_map = dict(out["top_words"])
    assert count_map.get("the") == 3 and count_map.get("fox") == 2, f"top words: {out['top_words']}"
    print("PASS /text/stats")

    # 3. /slug
    assert slugify("Hello, World!") == "hello-world", "basic slug"
    assert slugify("Café — Menus & Drinks") == "cafe-menus-drinks", "unicode slug"
    assert slugify("  Über  10x  Cool!  ") == "uber-10x-cool", "trim slug"
    assert slugify("!!!---###") == "", "empty slug from punctuation"
    print("PASS /slug")

    print("\nAll tests passed." if ok else "\nFAILURES detected.")


if __name__ == "__main__":
    _test()
