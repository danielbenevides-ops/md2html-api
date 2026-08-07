# MD2HTML API

Convert Markdown to styled HTML via a simple HTTP API.

## What It Does

MD2HTML API transforms Markdown text into clean, styled HTML. Send Markdown, get back ready-to-render HTML with standard styling applied. Perfect for blogs, docs, and content pipelines.

## Getting Started

1. Ensure the server is running locally on port 8777.
2. Obtain an API key (crypto payment required — see Pricing).
3. Send a POST request with your Markdown payload.
4. Receive styled HTML in the response.

```bash
# Start the server (if not already running)
python server.py
```

## How to Call It

```bash
curl -X POST http://localhost:8777/convert \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"markdown": "# Hello World\n\nThis is **bold** text."}'
```

**Response:**
```json
{
  "html": "<h1>Hello World</h1>\n<p>This is <strong>bold</strong> text.</p>"
}
```

## Pricing

| Plan | Cost | Payment |
|------|------|---------|
| Pay-per-call | $0.001 per call | Crypto (BTC/ETH/USDC) |

API keys are issued after your first crypto payment. Contact the operator for a wallet address and key provisioning.

## Configuration

- **Port:** 8777 (default)
- **Endpoint:** `POST /convert`
- **Auth:** Bearer token

---

Built as part of an autonomous business product. Production-ready, free-tier available.
