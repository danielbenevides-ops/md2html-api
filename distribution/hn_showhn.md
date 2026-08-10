# Show HN: I built a markdown-to-HTML API with micro-payments

Hey HN,

I built a simple API that converts Markdown to HTML. Send Markdown in, get clean HTML back. No auth, no API keys — just pay per request in Litecoin.

**What it does**

- POST your Markdown to `/md2html/`, get HTML returned
- Supports CommonMark + GFM (tables, fenced code, strikethrough)
- Zero state, zero tracking, zero accounts
- Live endpoint: http://147.15.103.217/md2html/

**Tech stack**

- Python stdlib `http.server` — no Flask, no FastAPI, no deps
- nginx reverse proxy in front
- systemd service unit for uptime
- Oracle Cloud ARM VPS (free tier, Ampere A1)

**Billing model**

Micro-payments in Litecoin (LTC). You load a wallet balance, each request deducts a small amount. No subscriptions, no monthly minimums. Idea: make it cheap enough you don't think about it, but nonzero so spam isn't free.

Why LTC over BTC/lightning? Low fees, fast confirms, dead simple to accept with a basic RPC node. Lightning is great but adds operational complexity I didn't need for a single-endpoint service.

**Links**

- API: http://147.15.103.217/md2html/
- Source: https://github.com/dcn13l/md2html-api

Happy to answer questions. Particularly interested in feedback on the billing approach — is LTC micropayments a reasonable model for a tiny utility API, or should I just go flat-rate / free-with-limits?
