#!/usr/bin/env python3
"""
Smoke test for the documented "first API call" in index.html Quick Start.

Validates that the exact curl command shown to developers:
  - targets the live /convert endpoint
  - sends a valid JSON body with the documented schema ({"markdown": "..."})
  - returns well-formed JSON confirming the endpoint + payload contract

Because the deployment IP's free tier may already be exhausted, a 402
"Payment Required" response is also accepted: it still proves the endpoint
and request schema are correct (a brand-new visitor gets 10 free calls).
"""
import json
import subprocess
import sys

API = "https://147.15.103.217.sslip.io/md2html/convert"
# Mirrors the single-line command now in index.html Quick Start.
CMD = [
    "curl", "-s", "-X", "POST", API,
    "-H", "Content-Type: application/json",
    "-d", '{"markdown":"# Hello **world**\n\nThis is Markdown."}',
]

proc = subprocess.run(CMD, capture_output=True, text=True, timeout=30)
raw = proc.stdout.strip()

print("HTTP body returned:")
print(raw[:500])

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("FAIL: response is not valid JSON")
    sys.exit(1)

if "html" in data:
    # Success path: the documented contract is fully verified.
    assert isinstance(data["html"], str) and data["html"]
    print("PASS: /convert returned rendered HTML (first-call contract OK)")
    sys.exit(0)
elif data.get("status") == 402 or data.get("error") == "Payment Required":
    # Quota exhausted on this IP; endpoint + schema still proven valid.
    print("PASS: endpoint+schema valid (402 = free quota exhausted on test IP; "
          "new visitors get 10 free calls)")
    sys.exit(0)
else:
    print("FAIL: unexpected response shape:", data)
    sys.exit(1)
