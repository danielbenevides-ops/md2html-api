#!/usr/bin/env python3
"""Verify FAQPage JSON-LD question text exactly matches visible FAQ summaries.

Google FAQ rich-result policy requires the structured-data questions to be
visible on the page and to match the on-page text. A mismatch silently
disqualifies the rich result. This test guards that invariant.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"


def load_faq_jsonld(html: str) -> dict:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "FAQPage":
            return data
    raise AssertionError("FAQPage JSON-LD block not found / invalid JSON")


def visible_faq_summaries(html: str):
    # <details><summary>Question?</summary> ... </details>
    return [m.strip() for m in re.findall(r"<summary>(.*?)</summary>", html, re.S)]


def main():
    html = HTML.read_text(encoding="utf-8")
    faq = load_faq_jsonld(html)
    names = [q["name"].strip() for q in faq["mainEntity"]]
    summaries = visible_faq_summaries(html)

    assert names, "No FAQ questions parsed from JSON-LD"
    assert summaries, "No visible FAQ summaries parsed from HTML"

    missing = [n for n in names if n not in summaries]
    extra = [s for s in summaries if s not in names]

    print(f"JSON-LD FAQ questions ({len(names)}): {names}")
    print(f"Visible FAQ summaries ({len(summaries)}): {summaries}")

    if missing or extra:
        print(f"FAIL: JSON-LD/visible mismatch. missing={missing} extra={extra}")
        sys.exit(1)

    print("PASS: every JSON-LD FAQ question exactly matches a visible FAQ summary")
    sys.exit(0)


if __name__ == "__main__":
    main()
