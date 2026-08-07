# MD2HTML API

> Convert Markdown to clean, styled HTML via a simple HTTP API. Stdlib-only, no dependencies, production-ready.

MD2HTML API transforms Markdown text into ready-to-render HTML with XSS-safe escaping, URL sanitization, and standard styling applied. Perfect for blogs, docs, content pipelines, and static-site generators. The entire server runs on Python's standard library — zero dependencies, deploy anywhere Python exists.

---

## Table of Contents

- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [`POST /convert`](#post-convert)
  - [`GET /health`](#get-health)
  - [`GET /docs`](#get-docs)
  - [`GET /payment`](#get-payment)
  - [`GET /usage`](#get-usage)
  - [`GET /stats`](#get-stats)
- [Code Examples](#code-examples)
  - [curl](#curl)
  - [JavaScript (fetch)](#javascript-fetch)
- [Pricing](#pricing)
- [Rate Limiting & Security](#rate-limiting--security)
- [Self-Host](#self-host)
  - [Deploy to VPS](#deploy-to-vps)
- [License](#license)

---

## Quick Start

```bash
# Clone
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api

# Run (Python only — no pip install needed)
python server.py
# → Markdown-to-HTML API on http://0.0.0.0:8777
```

First 10 calls per IP are free. Send a Markdown payload, get HTML back:

```bash
curl -X POST http://localhost:8777/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**"}'
```

---

## API Reference

Base URL: `http://localhost:8777` (or your deployed domain)

### `POST /convert`

Convert Markdown to HTML. Supported syntax: headings (`#`–`######`), **bold**, *italic*, `[links](url)`, `inline code`, fenced code blocks (` ``` `), and unordered lists.

**Request**

| Header          | Value                  | Required |
|-----------------|------------------------|----------|
| `Content-Type`  | `application/json` *or* `text/plain` | No |

**Body — JSON:**
```json
{
  "markdown": "# Hello **world**"
}
```

**Body — Raw text:**
```
# Hello **world**
```

**Response `200 OK`:**
```json
{
  "html": "<h1>Hello <strong>world</strong></h1>",
  "billing": {
    "status": "ok",
    "call_count": 1,
    "remaining": 9
  }
}
```

**Response `402 Payment Required`** (free tier exhausted):
```json
{
  "status": 402,
  "error": "Free tier exceeded",
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "currency": "LTC",
  "message": "Send Litecoin to continue. Free tier: 10 calls per IP."
}
```

**Response `413 Payload Too Large`:**
```json
{ "error": "Request body too large", "max_bytes": 1048576 }
```

**Response `429 Too Many Requests`:**
```json
{ "error": "Rate limit exceeded", "retry_after": 60 }
```

---

### `GET /health`

Health check / readiness probe.

**Response `200 OK`:**
```json
{ "status": "ok" }
```

---

### `GET /docs`

Returns a plain-text usage guide for the entire API.

**Response `200 OK`:** `text/plain` guide document.

---

### `GET /payment`

Returns the Litecoin wallet address for pay-per-call billing.

**Response `200 OK`:**
```json
{
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "currency": "LTC",
  "message": "Send any amount of Litecoin to this address to continue using the API after the free tier."
}
```

---

### `GET /usage`

Returns your current usage and remaining free-tier calls (tracked per IP).

**Response `200 OK`:**
```json
{
  "client": "203.0.113.42",
  "calls_made": 7,
  "free_tier_limit": 10,
  "remaining": 3
}
```

---

### `GET /stats`

Returns aggregate API statistics for the deployment. Useful for operators monitoring usage.

**Response `200 OK`:**
```json
{
  "total_calls": 1523,
  "unique_ips": 47,
  "daily": { ... }
}
```

---

## Code Examples

### curl

**Convert Markdown:**
```bash
curl -X POST http://localhost:8777/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Title\n\nParagraph with **bold** and *italic*.\n\n- Item one\n- Item two\n\n[Link](https://example.com)"}'
```

**Raw Markdown body (no JSON):**
```bash
curl -X POST http://localhost:8777/convert \
  -H "Content-Type: text/plain" \
  -d '# Heading

Some **bold** text.'
```

**Check usage:**
```bash
curl http://localhost:8777/usage
```

**Get payment address:**
```bash
curl http://localhost:8777/payment
```

**Health check:**
```bash
curl http://localhost:8777/health
```

### JavaScript (fetch)

**Convert Markdown:**
```javascript
const response = await fetch("http://localhost:8777/convert", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    markdown: "# Title\n\nParagraph with **bold** and *italic*.\n\n- Item one\n- Item two\n\n[Link](https://example.com)"
  }),
});

const data = await response.json();
console.log(data.html);
// <h1>Title</h1><p>Paragraph with <strong>bold</strong> ...</p>
console.log(data.billing.remaining);
```

**Catch 402 (payment required) and 429 (rate-limited):**
```javascript
async function convert(markdown) {
  const res = await fetch("http://localhost:8777/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });

  if (res.status === 402) {
    const billing = await res.json();
    console.error(`Free tier exceeded. Pay to: ${billing.wallet_address}`);
    return null;
  }

  if (res.status === 429) {
    const retry = (await res.json()).retry_after;
    console.error(`Rate-limited. Retry in ${retry}s`);
    return null;
  }

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()).html;
}
```

---

## Pricing

| Tier | Cost | Payment |
|------|------|--------|
| **Free** | 10 calls per IP | None |
| **Pay-per-call** | After free tier | Litecoin (LTC) |

There is no signup, no subscription, and no API key management — usage is tracked per IP automatically.

### How to pay

1. Call `GET /payment` to confirm the wallet address (or use the one below).
2. Send any amount of **Litecoin (LTC)** to:

   ```
   Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM
   ```

3. Payments enable continued usage. The more you send, the more calls you unlock.

The wallet address is also returned dynamically by the API — always verify it programmatically before sending funds.

---

## Rate Limiting & Security

| Feature | Value |
|---------|-------|
| Rate limit | 30 requests / minute per IP |
| Max body size | 1 MB |
| XSS protection | HTML-escaped input; `javascript:`/`data:`/`vbscript:` URLs blocked |
| Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` |
| CORS | `Access-Control-Allow-Origin: *` (configured for public use) |
| Dependencies | **None** — Python standard library only |
| Port | `8777` |

---

## Self-Host

MD2HTML API has zero external dependencies — if you have Python, you can run it. This makes it ideal for self-hosting on a VPS.

### Deploy to VPS

Tested on Ubuntu 22.04+ with Python 3.8+. Adapt commands as needed for your distro.

**1. SSH into your server and clone the repo:**

```bash
ssh root@your-vps-ip
apt update && apt install -y python3 git curl
git clone https://github.com/dcn13l/md2html-api.git /opt/md2html-api
cd /opt/md2html-api
```

**2. Start the server (test run):**

```bash
python3 server.py
# → Markdown-to-HTML API on http://0.0.0.0:8777
# Verify from another terminal:
curl http://localhost:8777/health
# → {"status": "ok"}
```

**3. Run as a systemd service (recommended for production):**

```bash
cat > /etc/systemd/system/md2html-api.service <<'EOF'
[Unit]
Description=MD2HTML API
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/md2html-api
ExecStart=/usr/bin/python3 /opt/md2html-api/server.py
Restart=always
RestartSec=3
User=www-data
Group=www-data
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now md2html-api
systemctl status md2html-api
```

**4. Expose on port 80 / 443 with a reverse proxy:**

The API listens on `127.0.0.1:8777` internally. Use NGINX or Caddy to proxy public traffic.

**NGINX** — `/etc/nginx/sites-available/md2html-api`:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8777;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
```bash
ln -s /etc/nginx/sites-available/md2html-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**Caddy** — `/etc/caddy/Caddyfile` (auto-HTTPS):
```
api.yourdomain.com {
    reverse_proxy 127.0.0.1:8777
}
```
```bash
sudo systemctl reload caddy
```

**5. Verify your deployment:**

```bash
curl http://api.yourdomain.com/health
# → {"status": "ok"}

curl -X POST http://api.yourdomain.com/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Deployed!"}'
# → {"html": "<h1>Deployed!</h1>", "billing": {"remaining": 9, ...}}
```

**Manage:**

```bash
# Using the included deploy.sh helper:
./deploy.sh start    # background start
./deploy.sh stop     # stop
./deploy.sh status   # health check

# Or via systemd:
systemctl restart md2html-api
journalctl -u md2html-api -f   # live logs
```

---

## License

MIT — see repository for details.

---

Built as part of an autonomous business product. [Source on GitHub](https://github.com/dcn13l/md2html-api).
