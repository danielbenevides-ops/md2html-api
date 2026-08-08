# MD2HTML API

> Convert Markdown to clean, styled HTML via a simple HTTP API. Zero dependencies — Python stdlib only.

**Live:** [http://147.15.103.217/md2html/](http://147.15.103.217/md2html/)  ·  [Source](https://github.com/dcn13l/md2html-api)  ·  License: MIT

MD2HTML API transforms Markdown text into ready-to-render HTML with XSS-safe escaping, URL sanitization, and standard styling. Ideal for blogs, docs, content pipelines, and static-site generators. Beyond the core converter, the service ships JSON prettification, text statistics, and URL slug generation — all from a single stdlib-only server.

## Quick Start

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**"}'
# {"html":"<h1>Hello <strong>world</strong></h1>","billing":{"status":"ok","call_count":1,"remaining":9}}
```

That's it — 10 free calls per IP, no API key required. See the [API Reference](#api-reference) for all 9 endpoints.

---

## Autonomous Business Experiment

MD2HTML API is a product of a **15-agent autonomous business team** orchestrated by [Hermes Agent](https://hermes-agent.nousresearch.com/). The experiment launched with **$0 starting capital**: agents designed the product, wrote the code, hardened security, deployed to a VPS, and set up Litecoin billing — with no human intervention in the loop. Pay-per-call revenue funds further autonomous operation.

---

## API Reference

Base URL: `http://147.15.103.217/md2html` (or self-host on port `8777`)

### `GET /health`
Health / readiness probe.
```bash
curl http://147.15.103.217/md2html/health
# {"status":"ok"}
```

### `POST /convert`
Convert Markdown to styled HTML. Supports headings, bold, italic, links, inline code, fenced code blocks, and lists. Body: JSON `{"markdown": "..."}` or raw `text/plain`.
```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**"}'
# {"html":"<h1>Hello <strong>world</strong></h1>","billing":{"status":"ok","call_count":1,"remaining":9}}
```

### `GET /payment`
Returns the Litecoin wallet address for pay-per-call billing.
```bash
curl http://147.15.103.217/md2html/payment
# {"wallet_address":"Las7JLihEnYvACUt4jgxqcFZrD3RgVM","currency":"LTC","message":"Send any amount of Litecoin..."}
```

### `GET /usage`
Current usage and remaining free-tier calls (tracked per IP).
```bash
curl http://147.15.103.217/md2html/usage
# {"client":"203.0.113.42","calls_made":7,"free_tier_limit":10,"remaining":3}
```

### `GET /stats`
Aggregate API statistics for the deployment.
```bash
curl http://147.15.103.217/md2html/stats
# {"total_calls":1523,"unique_ips":47,"daily":{...}}
```

### `GET /docs`
Plain-text usage guide for the entire API.
```bash
curl http://147.15.103.217/md2html/docs
```

### `POST /json/prettify`
Format and indent a JSON document.
```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -d '{"b":2,"a":1}'
# {"prettified":"{\n  \"a\": 1,\n  \"b\": 2\n}"}
```

### `POST /text/stats`
Compute word count, character count, and reading time for a text payload.
```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox."}'
# {"words":4,"characters":20,"reading_time_minutes":1}
```

### `POST /slug`
Generate a URL-safe slug from a title string.
```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World! My First Post"}'
# {"slug":"hello-world-my-first-post"}
```

---

## Pricing

| Tier | Cost | Payment |
|------|------|---------|
| **Free** | 10 calls per IP | None |
| **Pay-per-call** | $0.001 / call after free tier | Litecoin (LTC) |

No signup, subscription, or API keys — usage is tracked per IP automatically.

**How to pay:** Call `GET /payment` to verify the wallet, then send Litecoin (LTC) to `Las7JLihEnYvACUt4jgxqcFZrD3RgVM`. The more you send, the more calls you unlock. Always verify the address programmatically before sending funds.

---

## Security

| Feature | Value |
|---------|-------|
| Rate limit | 30 requests / minute per IP |
| Max body size | 1 MB (1048576 bytes) |
| XSS protection | HTML-escaped input; `javascript:`/`data:`/`vbscript:` URLs blocked |
| Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` |
| CORS | `Access-Control-Allow-Origin: *` (public use) |
| Authentication | Per-IP tracking, no keys |

Errors: `402 Payment Required` (free tier exceeded), `413 Payload Too Large`, `429 Too Many Requests`.

---

## Tech Stack

- **Language:** Python (3.8+)
- **Dependencies:** **None** — Python standard library only (`http.server`, `json`, `re`, `html`, `urllib`)
- **Server:** Single-file stdlib HTTP server, deployable anywhere Python runs
- **Deployment:** Systemd service behind a reverse proxy (NGINX/Caddy)

---

## Self-Host

```bash
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api
python3 server.py   # → http://0.0.0.0:8777
```

For production, run as a systemd service behind NGINX or Caddy. See the repo's `deploy.sh` helper.

---

Built as part of an autonomous business experiment by a 15-agent Hermes team starting from $0. [Source on GitHub](https://github.com/dcn13l/md2html-api).
