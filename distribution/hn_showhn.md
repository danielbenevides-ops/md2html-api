# Show HN: MD2HTML — a stdlib-only Markdown utility API on a free VPS

Hey HN,

I built and deployed MD2HTML, a small HTTP API for Markdown conversion and related text/HTML utilities. The server uses Python's standard library (`http.server`) behind nginx and systemd on an Oracle Cloud Always Free ARM VPS.

A tested first call:

```bash
curl -X POST https://147.15.103.217.sslip.io/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Hello\n\nThis is **bold**."}'
```

The service currently exposes 26 product endpoints, including conversion, sanitization, batch conversion, Markdown linting, HTML minification, table parsing, JSON formatting, text stats, slugs, and webhooks. The machine-readable contract is at:

https://147.15.103.217.sslip.io/md2html/swagger.json

The trial is 10 billable calls per IP or API key. After exhaustion, billable POST requests return HTTP 402 with LTC payment instructions. There is also a 30-request/minute per-IP rate limit.

The public deployment is HTTP-only right now, so I would not use it for sensitive data. I'm mainly looking for feedback on the API contract, onboarding flow, and whether sub-cent metering is useful for a utility this small.
