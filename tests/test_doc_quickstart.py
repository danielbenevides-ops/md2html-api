#!/usr/bin/env python3
"""Regression test for docs onboarding copy-paste validity.

Guards against the highest-ROI onboarding defects:
  * literal ``***`` placeholders left in public quickstart commands
    (e.g. the X-API-Key header in index.html's Quick Start).
  * malformed / mislabeled shell snippets: every ```bash fenced block in
    the public docs must be syntactically valid bash (``bash -n``).

Offline + deterministic (no network); validates the exact snippets a
developer copies, not a live call.
"""
import os
import re
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOC_FILES = [
    "docs/API_REFERENCE.md",
    "README.md",
    "INTEGRATION.md",
    "PRICING_TIERS.md",
    "blog/markdown-to-html-api-comparison.md",
    "distribution/devto_article.md",
]


def bash_blocks(text):
    return re.findall(r"```bash\n(.*?)```", text, re.S)


class DocQuickstartSanity(unittest.TestCase):
    def test_no_literal_star_placeholder_in_public_quickstart(self):
        with open(os.path.join(REPO, "index.html"), encoding="utf-8") as fh:
            html = fh.read()
        self.assertNotIn(
            '"X-API-Key: ***"',
            html,
            "index.html Quick Start still shows a literal '***' key "
            "placeholder in a copy-pasteable command.",
        )
        self.assertIn(
            "mk_YOUR_KEY_HERE",
            html,
            "index.html Quick Start should demonstrate a clear key placeholder.",
        )
        for rel in DOC_FILES:
            with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
                t = fh.read()
            self.assertNotIn(
                "***", t, f"{rel} contains a literal '***' placeholder"
            )

    def test_bash_blocks_are_valid(self):
        total = 0
        for rel in DOC_FILES:
            with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
                text = fh.read()
            for i, block in enumerate(bash_blocks(text)):
                total += 1
                # normalise CRLF (storage artifact, not command logic);
                # pass as raw bytes so cygwin's text-mode pipe translation
                # does not reintroduce \r.
                block = block.replace("\r", "")
                proc = subprocess.run(
                    ["bash", "-n", "-s"],
                    input=block.encode("utf-8"),
                    capture_output=True,
                )
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"{rel} bash block #{i} failed shell syntax check:\n"
                    f"{proc.stderr}\n--- block ---\n{block}",
                )
        self.assertGreater(total, 0, "no bash blocks found to validate")


if __name__ == "__main__":
    unittest.main()
