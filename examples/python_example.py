#!/usr/bin/env python3
"""MD2HTML API examples: /convert and /slug endpoints."""
import requests

BASE_URL = "https://147.15.103.217.sslip.io/md2html"
API_KEY = "YOUR_LTC_API_KEY"  # LTC address used as API key

# Convert Markdown to HTML
# POST /convert — send markdown, get HTML back
md_content = "# Hello\n\nThis is **bold** and *italic*."
resp = requests.post(
    f"{BASE_URL}/convert",
    json={"markdown": md_content, "api_key": API_KEY},
    timeout=30,
)
print("HTML:", resp.json()["html"])

# Generate URL-safe slug from text
# POST /slug — send text, get slug back
text = "Hello World! This is a Test."
resp = requests.post(
    f"{BASE_URL}/slug",
    json={"text": text, "api_key": API_KEY},
    timeout=30,
)
print("Slug:", resp.json()["slug"])
