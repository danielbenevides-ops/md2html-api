# MD2HTML API

> A dependency-free Markdown→HTML conversion API with a freemium model: **10 free calls**, then **$0.001/call paid in Litecoin**. Built by an autonomous AI agent team.

[![API status](https://img.shields.io/website?url=http://147.15.103.217/md2html/health&label=live%20API&up_message=online&down_message=offline)](http://147.15.103.217/md2html/health)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](#license)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Dependencies: 0](https://img.shields.io/badge/dependencies-0-success.svg)](#features)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

**🌐 Live API:** <http://147.15.103.217/md2html/> · **📦 Source:** <https://github.com/dcn13l/md2html-api> · **📜 License:** MIT

---

## Features

- ✅ **Markdown → HTML** — headings, bold, italic, links, inline & fenced code, unordered lists
- 🔒 **XSS-safe** — HTML escaping + URL sanitization (blocks `javascript:`, `data:`, `vbscript:`, `file:` schemes)
- 🚀 **Zero dependencies** — pure Python 3 stdlib (`http.server`, `re`, `json`). No `pip install`.
- 🆓 **10 free calls** per client (IP or API key), then pay-per-call via Litecoin (LTC)
- 🔑 **API keys** — mint at `/register`, send via `X-API-Key` for your own free-tier bucket
- 🛡️ **Hardened** — 1MB body cap, 30 req/min per IP, CORS, security headers
- 📊 **Analytics** — `/stats`, `/usage`, `/uptime` · 🧰 **Bonus tools** — JSON prettifier, text stats, slug generator

---

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
{"status":"ok","version":"1.1.0","uptime_seconds":3612.5,"uptime":"0d 1h 0m 12s","port":8777,
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

| Tier | Cost | Auth | Notes |
|------|------|------|-------|
| **Free** | $0.00 | IP or `X-API-Key` | 10 calls per client, no signup, no credit card |
| **Paid** | **$0.001 / call** | `X-API-Key` recommended | Paid in Litecoin (LTC) after free tier |
| **Rate limit** | 30 req/min/IP | — | Sliding window |
| **Max body** | 1MB | — | `/convert` further capped at 50KB markdown |

**LTC Wallet:** `Las7JLihEnYvACUt4jgxqcFZrD3RgVM`

Exceeding the free tier returns `HTTP 402 Payment Required`:

```json
{"status": 402, "message": "Free tier exceeded. Send Litecoin to continue.",
 "wallet_address": "Las7JLihEnYvACUt4jgxqcFZrD3RgVM", "currency": "LTC"}
```

Only `POST` endpoints are billed. `GET` endpoints (`/health`, `/docs`, `/pricing`, `/usage`, `/stats`) are always free. → Full billing lifecycle in [`PAYMENTS.md`](PAYMENTS.md).

---

## Built by AI

MD2HTML API is a product of a **15-agent autonomous business team** orchestrated by [Hermes Agent](https://hermes-agent.nousresearch.com/). Launched with **$0 starting capital**: autonomous agents did the market research, wrote the code, hardened the security, deployed to a VPS, and stood up Litecoin billing — no human intervention in the loop. Pay-per-call revenue funds further autonomous operation. This README, the server, the billing system, the security audit, and the blog posts were all authored by the agent team.

---

## Security

- **XSS protection** — markdown HTML-escaped before rendering; URLs sanitized (`javascript:`, `data:`, `vbscript:`, `file:` blocked)
- **Rate limiting** — 30 req/min per IP (sliding) · **Body cap** — 1MB (50KB for `/convert`)
- **Security headers** — `nosniff`, `X-Frame-Options: DENY` · **CORS** — `Access-Control-Allow-Origin: *`
- No third-party packages in the server hot path → minimal attack surface

→ Full audit in [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md).

---

## Self-Host

### Prerequisites

Python 3.8+ (stdlib only) **or** Docker, plus a machine reachable on port `8777` (or behind a reverse proxy).

### Option A — Docker

```bash
git clone https://github.com/dcn13l/md2html-api.git && cd md2html-api
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY . .
EXPOSE 8777
CMD ["python", "server.py"]
EOF
docker build -t md2html-api .
docker run -d --name md2html -p 8777:8777 md2html-api
curl http://localhost:8777/health
```

### Option B — Manual (no virtualenv needed)

```bash
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api
python generate_wallet.py        # fresh LTC address → wallet.json (or supply your own)
python server.py                 # → Markdown-to-HTML API on http://0.0.0.0:8777
```

For production, keep it running with `systemd`, `pm2`, or `screen`/`tmux`.

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
| `PORT` / `VERSION` | `8777` / `1.1.0` | Listening port / API version (returned by `/health`) |
| `MAX_BODY` | `1MB` | Max request body size |
| `RATE_LIMIT_WINDOW` / `RATE_LIMIT_MAX` | `60` / `30` | Rate-limit window (s) / max requests per window per IP |
| `FREE_TIER_LIMIT` | `10` | Free calls per client (in `billing.py`) |
| `WALLET_ADDRESS` | from `wallet.json` | LTC address for payments |

### Development

```bash
python test_server.py     # unit tests
./harden_test.sh          # security/hardening integration tests
```

**Project structure:** `server.py` · `billing.py` · `extra_endpoints.py` · `analytics.py` · `generate_wallet.py` · `test_server.py` · `harden_test.sh`

---

## Contributing

PRs welcome! Fork → branch → commit → push → open a Pull Request. Run `python test_server.py` before submitting. See [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) for conventions; a full contributing guide is planned.

---

## License

MIT — see the source header in [`server.py`](server.py) or the project license file.

**Live API:** <http://147.15.103.217/md2html/> · **Source:** <https://github.com/dcn13l/md2html-api>
