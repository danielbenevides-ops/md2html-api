# MD2HTML API

[![LIVE API](https://img.shields.io/website?url=http%3A%2F%2F147.15.103.217%2Fmd2html%2Fhealth&label=LIVE%20API&style=for-the-badge)](http://147.15.103.217/md2html/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-2ea44f)](#features)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f)](#license)
[![GitHub stars](https://img.shields.io/github/stars/dcn13l/md2html-api?style=social)](https://github.com/dcn13l/md2html-api/stargazers)

> Convert Markdown to clean HTML and use a practical set of developer utilities over HTTP. **Python standard library only. No pip install. No subscriptions.**

**Live API:** <http://147.15.103.217/md2html/>
**Repository:** <https://github.com/dcn13l/md2html-api>
**Release:** `v1.3.0` — 18 endpoints, LTC micropayments, and an enhanced landing page

## ⭐ Stargazers

If MD2HTML API is useful, [star the repository](https://github.com/dcn13l/md2html-api) to help other developers discover this zero-dependency Markdown→HTML API.

[View all stargazers](https://github.com/dcn13l/md2html-api/stargazers) · [Watch releases](https://github.com/dcn13l/md2html-api/subscription)

## Why MD2HTML?


- **Simple:** send JSON or plain text and receive JSON back.
- **Useful:** Markdown conversion plus sanitization, batching, code minification, HTML extraction, URL shortening, cron parsing, regex testing, JSON formatting, text statistics, and slug generation.
- **Safe by default:** HTML escaping, URL-scheme filtering, request-size limits, CORS, and security headers.
- **Low-friction:** 10 free calls per client, with no signup required for the free tier.
- **Predictable:** pay only when you need more calls, at `$0.001` per call in Litecoin (LTC).
- **Portable:** the server uses only Python's standard library and runs anywhere Python 3.8+ runs.

## Quick Start

No signup, no API key — 10 free calls per IP:

```bash
# 1. Health check
curl http://147.15.103.217/md2html/health
# 2. Convert Markdown to HTML
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**\n\n- item 1\n- item 2"}'
# 3. Mint your own API key (separate free-tier bucket)
curl http://147.15.103.217/md2html/register
```

Want to self-host? Jump to [Self-Host](#self-host).

---

## API Reference

**Base URL:** `http://147.15.103.217/md2html` · **Port:** `8777` · **Rate limit:** 30 req/min/IP · **Max body:** 1MB

Only `POST` endpoints (`/convert`, `/json/prettify`, `/text/stats`, `/slug`) are billed. All `GET` endpoints are free. Add `-H "X-API-Key: <key>"` to bill against your key rather than your IP.

| # | Method | Endpoint | Billed | Description |
|---|--------|----------|:------:|-------------|
| 1 | `GET`  | `/health` | — | Readiness probe: status, version, uptime, endpoint manifest |
| 2 | `GET`  | `/register` | — | Mint a new API key (own free-tier bucket) |
| 3 | `POST` | `/convert` | ✓ | Convert Markdown to styled HTML (max 50KB markdown) |
| 4 | `POST` | `/json/prettify` | ✓ | Pretty-print a compact JSON document |
| 5 | `POST` | `/text/stats` | ✓ | Word count, char count, reading time, top words |
| 6 | `POST` | `/slug` | ✓ | Generate a URL-safe slug from a title |
| 7 | `GET`  | `/docs` | — | Plain-text usage guide for the entire API |
| 8 | `GET`  | `/pricing` | — | Public plan and rate-limit information |
| 9 | `GET`  | `/payment` | — | LTC wallet address for pay-per-call billing |
| 10 | `GET` | `/usage` | — | Current usage and remaining free-tier calls |

### 1. `GET /health`

```bash
curl http://147.15.103.217/md2html/health
```
```json
{"status":"ok","version":"1.4.0","uptime_seconds":3612.5,"uptime":"0d 1h 0m 12s","port":8777,
 "endpoints":["/health","/register","/convert","/json/prettify","/text/stats","/slug","/docs","/pricing","/payment","/usage","/stats"]}
```

### 2. `GET /register`

```bash
curl http://147.15.103.217/md2html/register
```
```json
{"api_key":"mk_abc123def456","wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM",
 "free_tier_limit":10,"calls_made":0,"remaining":10}
```

### 3. `POST /convert`

Supports headings, bold, italic, links, inline code, fenced code blocks, unordered lists. Body: `application/json` (`{"markdown": "..."}`) or `text/plain` (raw markdown). Max markdown input: 50KB.

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**\n\nVisit [example](https://example.com)."}'
```
```json
{"html":"<h1>Hello <strong>world</strong></h1>\n<p>Visit <a href=\"https://example.com\">example</a>.</p>",
 "billing":{"status":"ok","call_count":1,"remaining":9}}
```

### 4. `POST /json/prettify`

Input JSON string goes in the `"json"` field (not the request body itself).

```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"b\":2,\"a\":1}"}'
```
```json
{"prettified":"{\n  \"a\": 1,\n  \"b\": 2\n}","billing":{"status":"ok","call_count":3,"remaining":7}}
```

### 5. `POST /text/stats`

```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
```
```json
{"words":9,"chars":44,"chars_no_spaces":35,"reading_time_min":0.05,
 "top_words":[["the",2],["quick",1]],"billing":{"status":"ok","call_count":4,"remaining":6}}
```

### 6. `POST /slug`

Input goes in the `"title"` field. Handles non-ASCII and special characters.

```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -d '{"title": "Café — Menus & Drinks!"}'
```
```json
{"slug":"cafe-menus-drinks","billing":{"status":"ok","call_count":5,"remaining":5}}
```

### 7. `GET /docs`

```bash
curl http://147.15.103.217/md2html/docs
```

### 8. `GET /pricing`

No auth, not billed.

```bash
curl http://147.15.103.217/md2html/pricing
```
```json
{"free_tier":{"calls":10,"price_per_call":"0.00 USD","auth":"none — identified by IP or X-API-Key"},
 "paid_tier":{"price_per_call":"0.001 USD","currency":"LTC","wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM"},
 "rate_limit":{"max":30,"window_seconds":60},"max_body_bytes":1048576}
```

### 9. `GET /payment`

```bash
curl http://147.15.103.217/md2html/payment
```
```json
{"wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM","currency":"LTC",
 "message":"Send any amount of Litecoin to this address to continue using the API after the free tier."}
```

### 10. `GET /usage`

Query by IP (no header) or by API key (`-H "X-API-Key: ..."`).

```bash
curl http://147.15.103.217/md2html/usage
```
```json
{"client":"203.0.113.42","calls_made":7,"free_tier_limit":10,"remaining":3}
```

---

## Pricing

| Plan | Price | Details |
|---|---:|---|
| Free tier | **$0** | 10 calls per client, identified by IP or `X-API-Key` |
| Pay per call | **$0.001/call** | Litecoin (LTC) micropayments after the free tier |

There are no subscriptions, credit cards, or third-party runtime dependencies. Billed `POST` operations return `HTTP 402 Payment Required` after the 10-call free tier and include the payment wallet. Public `GET` endpoints such as health, docs, pricing, usage, and statistics remain free.

- **LTC wallet:** `Las7JLihEnYvACUt4jgxqcFZrD3RgVM`
- **Rate limit:** 30 requests per minute per IP
- **Maximum request body:** 1 MiB (Markdown conversion is limited to 50 KiB)

See [`PAYMENTS.md`](PAYMENTS.md) for the billing lifecycle and payment verification details.

## Quick start

No API key is required for the first 10 calls:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello **world**\n\n- one\n- two"}'
```

Example response:

```json
{
  "html": "<h1>Hello <strong>world</strong></h1>\n\n<ul>\n<li>one</li>\n<li>two</li>\n</ul>",
  "billing": {"status": 200, "calls_made": 1, "remaining": 9, "free_tier_limit": 10}
}
```

To get a separate free-tier bucket, mint an API key:

```bash
curl http://147.15.103.217/md2html/register
# {"api_key":"mk_...","free_tier_limit":10,"calls_made":0,"remaining":10}

curl -X POST http://147.15.103.217/md2html/convert \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: mk_...' \
  -d '{"markdown":"## Keyed request"}'
```

### Python (standard library only)

```python
import json
from urllib.request import Request, urlopen

request = Request(
    "http://147.15.103.217/md2html/convert",
    data=json.dumps({"markdown": "# Hello **world**"}).encode(),
    headers={"Content-Type": "application/json"},
)
with urlopen(request) as response:
    print(json.load(response))
```

This example uses only the Python standard library; add an `X-API-Key` header when you want a separate free-tier bucket.

## API reference — 18 endpoints

The v1.3.0 core endpoint manifest contains the 18 routes below. All six utility/conversion operations added for the v1.3.0 release use the same billing model and accept an optional `X-API-Key` header.

| # | Method | Endpoint | Billing | Description |
|---:|---|---|---|---|
| 1 | `GET` | `/health` | Free | Readiness, version, uptime, limits, and the endpoint manifest |
| 2 | `GET` | `/register` | Free | Mint an API key for an independent free-tier bucket |
| 3 | `POST` | `/convert` | Billable | Convert Markdown to HTML; JSON or `text/plain` input |
| 4 | `POST` | `/sanitize` | Billable | Escape raw HTML in Markdown before converting it |
| 5 | `POST` | `/batch` | Billable | Convert up to 50 Markdown strings in one request |
| 6 | `POST` | `/minify` | Billable | Minify HTML, CSS, or JavaScript source |
| 7 | `POST` | `/html/extract` | Billable | Extract visible text from HTML |
| 8 | `POST` | `/url/shorten` | Billable | Create an idempotent base62 short code for an HTTP(S)/FTP URL |
| 9 | `POST` | `/cron/parse` | Billable | Turn a five-field cron expression into a human description |
| 10 | `POST` | `/regex/test` | Billable | Test a regular expression and return match details |
| 11 | `POST` | `/json/prettify` | Billable | Pretty-print a compact JSON document with two-space indentation |
| 12 | `POST` | `/text/stats` | Billable | Return word, character, reading-time, and top-word statistics |
| 13 | `POST` | `/slug` | Billable | Generate a URL-safe slug from a title |
| 14 | `GET` | `/docs` | Free | Plain-text usage guide with request examples |
| 15 | `GET` | `/pricing` | Free | Free-tier, LTC price, wallet, rate-limit, and body-limit details |
| 16 | `GET` | `/payment` | Free | LTC wallet and payment instructions |
| 17 | `GET` | `/usage` | Free | Current client usage and remaining free calls |
| 18 | `GET` | `/stats` | Free | Aggregate call and client statistics |

Additional operational routes are also available: `GET /swagger.json` (OpenAPI 3.0), `GET /uptime`, `GET /` and `GET /index.html` (enhanced landing page), and `OPTIONS` for CORS preflight.

### Conversion and content utilities

```bash
# Sanitize untrusted Markdown
curl -X POST http://147.15.103.217/md2html/sanitize \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello <script>alert(1)</script>"}'

# Batch conversion (up to 50 items)
curl -X POST http://147.15.103.217/md2html/batch \
  -H 'Content-Type: application/json' \
  -d '{"items":["# First","## Second"]}'

# Minify HTML, CSS, or JavaScript
curl -X POST http://147.15.103.217/md2html/minify \
  -H 'Content-Type: application/json' \
  -d '{"code":"<div>  Hello  </div>","type":"html"}'

# Extract visible text from HTML
curl -X POST http://147.15.103.217/md2html/html/extract \
  -H 'Content-Type: application/json' \
  -d '{"html":"<h1>Hello</h1><p>World</p>"}'
```

### Developer utilities

```bash
# Shorten a URL
curl -X POST http://147.15.103.217/md2html/url/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/a/long/path"}'

# Explain a cron expression
curl -X POST http://147.15.103.217/md2html/cron/parse \
  -H 'Content-Type: application/json' \
  -d '{"expression":"*/5 * * * *"}'

# Test a regular expression
curl -X POST http://147.15.103.217/md2html/regex/test \
  -H 'Content-Type: application/json' \
  -d '{"pattern":"\\d+","input":"abc 12 def 34","flags":"i"}'

# Pretty-print JSON, calculate text stats, or generate a slug
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H 'Content-Type: application/json' \
  -d '{"json":"{\"b\":2,\"a\":1}"}'
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H 'Content-Type: application/json' \
  -d '{"text":"The quick brown fox jumps over the lazy dog."}'
curl -X POST http://147.15.103.217/md2html/slug \
  -H 'Content-Type: application/json' \
  -d '{"title":"Café — Menus & Drinks!"}'
```

## Features

- Markdown headings, emphasis, links, inline code, fenced code blocks, and unordered lists
- XSS-safe HTML escaping and blocking of `javascript:`, `data:`, `vbscript:`, and `file:` URLs
- JSON, text, slug, minification, extraction, URL, cron, and regex utilities with consistent JSON responses
- Batch conversion with a 50-item limit and partial-result handling on payment exhaustion
- API-key registration with IP fallback for clients that do not use a key
- 30 requests/minute/IP rate limiting and a 1 MiB body cap
- CORS and security headers (`nosniff` and `DENY` frame policy)
- Built-in analytics, OpenAPI output, and an enhanced browser-friendly landing page

## Self-hosting

Requirements: Python 3.8 or newer. The server has no third-party runtime dependencies.

```bash
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api
python server.py
# Markdown-to-HTML API on http://0.0.0.0:8777
```

The local API is available at `http://localhost:8777/`. For production, put it behind a reverse proxy and keep the Litecoin wallet configuration outside source control where appropriate. See [`deploy.sh`](deploy.sh) and [`INTEGRATION.md`](INTEGRATION.md) for deployment and client examples.


## Development

### Behind an nginx reverse proxy

Mount under `/md2html/` (same path the live API uses):

```nginx
location /md2html/ {
    proxy_pass http://127.0.0.1:8777/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Configuration

Configured via constants at the top of [`server.py`](server.py):

| Constant | Default | Description |
|---|---|---|
| `PORT` / `VERSION` | `8777` / `1.4.0` | Listening port / API version (returned by `/health`) |
| `MAX_BODY` | `1MB` | Max request body size |
| `RATE_LIMIT_WINDOW` / `RATE_LIMIT_MAX` | `60` / `30` | Rate-limit window (s) / max requests per window per IP |
| `FREE_TIER_LIMIT` | `10` | Free calls per client (in `billing.py`) |
| `WALLET_ADDRESS` | from `wallet.json` | LTC address for payments |

### Development

```bash
python test_server.py
python test_new_endpoints.py
python -m py_compile server.py billing.py analytics.py extra_endpoints.py
```

Useful project files:

- `server.py` — HTTP routing, Markdown conversion, utilities, security, CORS, and limits
- `billing.py` — free-tier tracking and API-key registration
- `extra_endpoints.py` — JSON, text, and slug handlers
- `analytics.py` — call logging and aggregate statistics
- `index.html` — enhanced landing page and live demo
- `PAYMENTS.md` — Litecoin billing lifecycle
- `SECURITY_AUDIT.md` — security review

## Contributing

Issues and pull requests are welcome. Please run the test and compile commands above before submitting a change.

## License

MIT.

**Live API:** <http://147.15.103.217/md2html/> · **Source:** <https://github.com/dcn13l/md2html-api>
