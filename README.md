# MD2HTML API

<<<<<<< Updated upstream
A markdown-to-HTML conversion API with a freemium model. 10 free calls, then pay via Litecoin.

**Public API URL:** http://147.15.103.217/md2html/

## Getting Started

1. Register for an API key:
   ```bash
   curl -X POST http://147.15.103.217/md2html/register \
     -H "Content-Type: application/json" \
     -d '{"email":"you@example.com"}'
   ```
2. Use your API key in the `X-API-Key` header for all requests.
3. You get 10 free calls. After that, requests return `402 Payment Required`.
4. Pay by sending LTC to the wallet below; then call `/payment` to confirm.

## Pricing

| Tier | Cost |
|------|------|
| First 10 calls | Free |
| After 10 calls | 402 + LTC payment |
=======
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies: None](https://img.shields.io/badge/dependencies-0-success.svg)](#features)
[![API Status](https://img.shields.io/website?url=http://147.15.103.217/md2html/health&label=live%20API)](http://147.15.103.217/md2html/health)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

> Convert Markdown to clean, styled HTML via a simple HTTP API. **Zero dependencies — Python stdlib only.**

**🌍 Live API:** <http://147.15.103.217/md2html/>
**📦 Source:** <https://github.com/dcn13l/md2html-api>
**📜 License:** MIT

---

## ✨ Features

- ✅ **Markdown → HTML** — headings, bold, italic, links, inline & fenced code, unordered lists
- 🔒 **XSS-safe** — HTML escaping + URL sanitization (blocks `javascript:`, `data:`, `vbscript:`, `file:` schemes)
- 🚀 **Zero dependencies** — pure Python 3 stdlib (`http.server`, `re`, `json`). No pip install needed.
- 🆓 **10 free calls** per client (IP or API key), then pay-per-call via Litecoin
- 🔑 **API keys** — mint one at `/register`, send it via `X-API-Key` header for your own free-tier bucket
- 🛡️ **Hardened** — 1MB body cap, 30 req/min rate limit per IP, CORS, security headers
- 📊 **Built-in analytics** — `/stats`, `/usage`, `/uptime` for observability
- 🧰 **Bonus endpoints** — JSON prettifier, text stats, URL slug generator

---

## 🚀 Quick Start

No API key required — 10 free calls per IP to start:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**\n\n- item 1\n- item 2"}'

# {"html":"<h1>Hello <strong>world</strong></h1>\n<ul>\n<li>item 1</li>\n<li>item 2</li>\n</ul>","billing":{"status":"ok","call_count":1,"remaining":9}}
```

Want your own free-tier bucket (e.g. behind a shared IP)? Register first:

```bash
curl http://147.15.103.217/md2html/register
# {"api_key":"mk_abc123...","wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM","free_tier_limit":10,"calls_made":0,"remaining":10}

# Then send the key on every billed request:
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: mk_abc123..." \
  -d '{"markdown": "# Hello **world**"}'
```
>>>>>>> Stashed changes

**LTC Wallet:** `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`

<<<<<<< Updated upstream
## Endpoints

### 1. Health Check
```bash
curl http://147.15.103.217/md2html/health
```

### 2. Register
```bash
curl -X POST http://147.15.103.217/md2html/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
```

### 3. Convert Markdown to HTML
```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"markdown":"# Hello World"}'
```

### 4. JSON Prettify
```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"json":"{\"key\":\"value\"}"}'
```

### 5. Text Stats
```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

### 6. Slug Generator
=======
## 📖 API Reference

**Base URL:** `http://147.15.103.217/md2html` · **Self-host port:** `8777` · **Rate limit:** 30 req/min/IP · **Max body:** 1MB

### `GET /health`
Health / readiness probe. Returns status, version, uptime, and the endpoint manifest.

```bash
curl http://147.15.103.217/md2html/health
# {"status":"ok","version":"1.1.0","uptime_seconds":3612.5,"uptime":"0d 1h 0m 12s","port":8777,"endpoints":["/health","/register","/convert","/json/prettify","/text/stats","/slug","/docs","/pricing","/payment","/usage","/stats"]}
```

### `GET /register`
Mint a new API key. Use it via the `X-API-Key` header on billed requests to get
your own 10-call free tier (otherwise billing falls back to your IP address).

```bash
curl http://147.15.103.217/md2html/register
# {"api_key":"mk_abc123def456","wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM","free_tier_limit":10,"calls_made":0,"remaining":10}
```

### `POST /convert`
Convert Markdown to styled HTML. Supports headings, bold, italic, links,
inline code, fenced code blocks, and unordered lists.

| Header | Value |
|---|---|
| `Content-Type` | `application/json` (body `{"markdown": "..."}`) **or** `text/plain` (raw markdown) |
| `X-API-Key` | Optional — your key from `/register` |

**Max markdown input:** 50KB.

```bash
# JSON body
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**\n\nVisit [example](https://example.com)."}'
# {"html":"<h1>Hello <strong>world</strong></h1>\n<p>Visit <a href=\"https://example.com\">example</a>.</p>","billing":{"status":"ok","call_count":1,"remaining":9}}

# Raw markdown body (text/plain)
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: text/plain" \
  -d '# Hello **world**'
```

With a fenced code block:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "```python\nprint(\"hi\")\n```"}'
# {"html":"<pre><code>print("hi")</code></pre>","billing":{"status":"ok","call_count":2,"remaining":8}}
```

### `POST /json/prettify`
Re-indent a compact JSON document with 2-space pretty printing. Note: the
input JSON string goes in the `"json"` field, **not** the request body itself.

```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"b\":2,\"a\":1}"}'
# {"prettified":"{\n  \"a\": 1,\n  \"b\": 2\n}","billing":{"status":"ok","call_count":3,"remaining":7}}
```

### `POST /text/stats`
Compute word count, character count, reading time, and top words for a text payload.

```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
# {"words":9,"chars":44,"chars_no_spaces":35,"reading_time_min":0.05,"top_words":[["the",2],["quick",1],...],"billing":{"status":"ok","call_count":4,"remaining":6}}
```

### `POST /slug`
Generate a URL-safe slug from a title string. Note: the input goes in the
`"title"` field, **not** `"text"`.

```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello, World! My First Post"}'
# {"slug":"hello-world-my-first-post","billing":{"status":"ok","call_count":5,"remaining":5}}
```

```bash
# Non-ASCII and special characters are handled too:
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -d '{"title": "Café — Menus & Drinks!"}'
# {"slug":"cafe-menus-drinks","billing":{"status":"ok","call_count":6,"remaining":4}}
```

### `GET /docs`
Plain-text usage guide for the entire API.

```bash
curl http://147.15.103.217/md2html/docs
```

### `GET /pricing`
Public plan and rate-limit information (no auth, not billed).

```bash
curl http://147.15.103.217/md2html/pricing
# {"free_tier":{"calls":10,"price_per_call":"0.00 USD","auth":"none — identified by IP or X-API-Key"},
#  "paid_tier":{"price_per_call":"0.001 USD","currency":"LTC","wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM"},
#  "rate_limit":{"max":30,"window_seconds":60},"max_body_bytes":1048576}
```

### `GET /payment`
Returns the Litecoin wallet address for pay-per-call billing after the free tier.

```bash
curl http://147.15.103.217/md2html/payment
# {"wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM","currency":"LTC","message":"Send any amount of Litecoin to this address to continue using the API after the free tier."}
```

### `GET /usage`
Current usage and remaining free-tier calls for your client (IP or `X-API-Key`).

```bash
# By IP
curl http://147.15.103.217/md2html/usage
# {"client":"203.0.113.42","calls_made":7,"free_tier_limit":10,"remaining":3}

# By API key
curl -H "X-API-Key: mk_abc123..." http://147.15.103.217/md2html/usage
```

### `GET /stats`
Aggregate API statistics for the deployment.

>>>>>>> Stashed changes
```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text":"Hello World This Is A Title"}'
```

<<<<<<< Updated upstream
### 7. Docs
```bash
curl http://147.15.103.217/md2html/docs
```

### 8. Payment
```bash
curl -X POST http://147.15.103.217/md2html/payment \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"txid":"YOUR_LITECOIN_TX_ID","amount":0.01}'
```

### 9. Usage
```bash
curl http://147.15.103.217/md2html/usage \
  -H "X-API-Key: YOUR_API_KEY"
```

### 10. Stats
```bash
curl http://147.15.103.217/md2html/stats \
  -H "X-API-Key: YOUR_API_KEY"
=======
### `GET /uptime`
Lightweight uptime + call summary probe.

```bash
curl http://147.15.103.217/md2html/uptime
# {"uptime_seconds":3612.5,"total_calls":1523,"unique_ips":47}
>>>>>>> Stashed changes
```

## Repository

<<<<<<< Updated upstream
GitHub: [dcn13l/md2html-api](https://github.com/dcn13l/md2html-api)

## License

MIT
=======
## 💳 Billing

| | Details |
|---|---|
| **Free tier** | 10 free calls per client (IP or API key) — no signup, no credit card |
| **After free tier** | `HTTP 402 Payment Required` with the LTC wallet address |
| **Price** | $0.001 USD per call, paid in Litecoin (LTC) |
| **Wallet** | `Las7JLihEnYvACUt4jgxqcFZrD3RgVM` |
| **Client identity** | `X-API-Key` header (recommended) → falls back to caller IP |

When you exceed the free tier, billed endpoints respond:

```json
{"status": 402, "message": "Free tier exceeded. Send Litecoin to continue.", "wallet_address": "Las7JLihEnYvACUt4jgxqcFZrD3RgVM", "currency": "LTC"}
```

Only `POST` endpoints (`/convert`, `/json/prettify`, `/text/stats`, `/slug`) are
billed. GET endpoints like `/health`, `/docs`, `/pricing`, `/usage`, and `/stats`
are always free.

→ See [`PAYMENTS.md`](PAYMENTS.md) for the full billing lifecycle.

---

## 🛡️ Security

- **XSS protection** — all markdown is HTML-escaped before rendering; URLs sanitized against `javascript:`, `data:`, `vbscript:`, `file:` schemes
- **Rate limiting** — 30 requests/min per IP (sliding window)
- **Body cap** — 1MB max request body; `/convert` further capped at 50KB markdown input
- **Security headers** — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
- **CORS** — `Access-Control-Allow-Origin: *` (preflight via `OPTIONS`)
- No third-party packages in the server hot path → minimal attack surface

→ See [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) for the full audit.

---

## 🏗️ Self-Host

### Prerequisites

- Python 3.8+ (uses only the standard library — no `pip install` needed)
- A machine reachable on port `8777` (or behind a reverse proxy)

### Option A — Run directly

```bash
# Clone the repo
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api

# Generate a wallet.json (or supply your own Litecoin address)
python generate_wallet.py        # writes wallet.json with a fresh LTC address

# Start the server (no virtualenv, no dependencies required)
python server.py
# Markdown-to-HTML API on http://0.0.0.0:8777
#   Rate limit: 30 req/60s per IP
#   Body cap: 1048576 bytes
```

That's it — the API is live at `http://localhost:8777/`. Keep it running with
`systemd`, `pm2`, or `screen`/`tmux` for production.

### Option B — Docker

```bash
# Clone
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api

# Create a minimal Dockerfile (or use the included one if present)
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY . .
EXPOSE 8777
CMD ["python", "server.py"]
EOF

# Build & run
docker build -t md2html-api .
docker run -d --name md2html -p 8777:8777 md2html-api
curl http://localhost:8777/health
```

### Option C — systemd (Linux production)

```ini
# /etc/systemd/system/md2html.service
[Unit]
Description=MD2HTML API
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/md2html-api
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now md2html
sudo systemctl status md2html
```

### Behind a reverse proxy (nginx)

Use this pattern to mount MD2HTML under `/md2html/` (the same path the live API uses):

```nginx
location /md2html/ {
    proxy_pass http://127.0.0.1:8777/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Configuration

The server is configured via constants at the top of [`server.py`](server.py):

| Constant | Default | Description |
|---|---|---|
| `PORT` | `8777` | Listening port |
| `VERSION` | `1.1.0` | API version (returned by `/health`) |
| `MAX_BODY` | `1MB` | Max request body size |
| `RATE_LIMIT_WINDOW` | `60` | Rate-limit window in seconds |
| `RATE_LIMIT_MAX` | `30` | Max requests per window per IP |
| `FREE_TIER_LIMIT` | `10` | Free calls per client (in `billing.py`) |
| `WALLET_ADDRESS` | from `wallet.json` | LTC address for payments |

---

## 🧪 Development

```bash
# Run the test suite
python test_server.py

# Hardening/security test script
./harden_test.sh
```

### Project structure

```
server.py            # HTTP server: routing, billing, rate limiting, CORS, md_to_html()
billing.py           # Free-tier tracking, call recording, /register key minting
extra_endpoints.py   # /json/prettify, /text/stats, /slug handlers
analytics.py         # Call logging and aggregate /stats
check_balance.py     # Check the LTC wallet balance via Blockchair
generate_wallet.py   # Generate a fresh LTC wallet → wallet.json
deploy.sh            # VPS deployment helper
test_server.py       # Unit tests
harden_test.sh       # Security/hardening integration tests
index.html           # Landing page served at /
```

---

## 🤖 Autonomous Business Experiment

MD2HTML API is a product of a **15-agent autonomous business team** orchestrated
by [Hermes Agent](https://hermes-agent.nousresearch.com/). The experiment
launched with **$0 starting capital**: agents designed the product, wrote the
code, hardened security, deployed to a VPS, and set up Litecoin billing — with no
human intervention in the loop. Pay-per-call revenue funds further autonomous
operation.

---

## 📚 Related Docs

- [`PAYMENTS.md`](PAYMENTS.md) — Billing lifecycle, wallet setup, payment verification
- [`SECURITY_AUDIT.md`](SECURITY_AUDIT.md) — Full security audit report
- [`INTEGRATION.md`](INTEGRATION.md) — Integration guide with code examples
- [`WIKI.md`](WIKI.md) — Project wiki
- [`blog/`](blog/) — Technical blog posts on Markdown APIs

---

## Contributing

PRs are welcome! Please run `python test_server.py` before submitting.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) (or the source header in [`server.py`](server.py)).

**Live API:** <http://147.15.103.217/md2html/> · **Source:** <https://github.com/dcn13l/md2html-api>
>>>>>>> Stashed changes
