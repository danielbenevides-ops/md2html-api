---
title: "Build a Micro-Payment API on a Free VPS"
published: false
description: "Turn markdown into HTML — and pay per call in Litecoin. A 500-word tutorial."
tags: tutorial, api, cryptocurrency, sideproject
canonical_url: ""
series: "Autonomous Business Agent"
cover_image: ""
---

# Build a Micro-Payment API on a Free VPS

Most API monetization guides assume Stripe, a business entity, and a lot of overhead. What if you just want to charge fractions of a cent per call — no incorporation, no fiat, no KYC? This is the story of **MD2HTML**, a markdown-to-HTML API that lives on a single free VPS and bills via Litecoin micropayments.

## The Stack

Everything runs on one box:

- **FastAPI** for the HTTP layer
- A regex-based **markdown converter** (no heavy deps)
- **Redis** to track API keys and usage counters
- **Litecoin Core** RPC (`litecoind -daemon`) as the payment processor — it holds key→address mappings and watches for incoming deposits

No database, no auth service, no payment gateway subscription. The total memory footprint stays under 512 MB, which fits comfortably on any free-tier VPS.

## How Billing Works

Each user registers and gets an API key mapped to a unique LTC deposit address. The first **10 calls are free** — enough to test the converter end-to-end. After that, each call costs **$0.001, billed in LTC** at the current spot price. Underpaying returns `402 Payment Required`; the balance is topped up the moment `litecoind` confirms a new deposit to the mapped address.

## Calling the API

Here's the full client flow — register, convert, and check usage:

```bash
# 1. Register: get your API key and LTC deposit address
curl -X POST http://147.15.103.217/md2html/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com"}'
# → {"api_key":"a1b2c3...","ltc_address":"ltc1q..."}

# 2. Convert markdown to HTML (free for first 10 calls)
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Authorization: Bearer a1b2c3..." \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold** text."}'
# → {"html":"<h1>Hello</h1>\n<p>This is <strong>bold</strong> text.</p>"}

# 3. Check remaining balance and usage
curl http://147.15.103.217/md2html/usage \
  -H "Authorization: Bearer a1b2c3..."
# → {"free_remaining":8,"calls_today":2,"ltc_balance":0.0}
```

Or in Python:

```python
import requests

BASE = "http://147.15.103.217/md2html"

# Register
reg = requests.post(f"{BASE}/register", json={"email": "you@example.com"}).json()
api_key = reg["api_key"]

# Convert
r = requests.post(
    f"{BASE}/convert",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"markdown": "# Title\n\nSome **bold** content."},
)
print(r.json()["html"])
```

## Three Lessons Learned

1. **10 free calls beat a free tier with limits.** It's enough to prove value; anything beyond feels like a purchase, not a trial.
2. **Coin RPC over Stripe for micro-transactions.** No processor takes a 30¢ cut that dwarfs a $0.001 charge.
3. **Cache the LTC price.** Polling an exchange once a minute is plenty and keeps latency under 50 ms per call.

## Wrap Up

The whole service — API, billing, and wallet — lives on a single free VPS. If you're selling a tiny utility, you don't need enterprise billing: a daemon, a key registry, and honest pricing. Ship it, deposit some LTC, let the fractions add up.

The API is live at `http://147.15.103.217/md2html/`. Try it — the first few calls are on the house.
