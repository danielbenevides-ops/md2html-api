# I shipped a stdlib-only Markdown utility API on an Oracle free VPS

Hey r/SideProject,

I built **MD2HTML**, a small HTTP API that converts Markdown to HTML and provides related text/HTML utilities. It runs on an Oracle Cloud Always Free ARM VPS using Python's standard-library `http.server`, nginx, and systemd.

The public deployment currently reports version 1.4.0 and 26 product endpoints. Besides `/convert`, it includes sanitization, batch conversion, Markdown linting, HTML minification, table parsing, JSON formatting, text stats, slugs, and webhooks.

A real first call:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Hello\n\nThis is **bold**."}'
```

API contract:

http://147.15.103.217/md2html/swagger.json

The trial includes 10 billable calls per IP or API key. After that, billable POST requests return HTTP 402 with LTC payment information. The service enforces 30 requests per minute per source IP and a 1 MiB request-body limit.

One honest limitation: the public URL is HTTP-only today, so don't send sensitive content. I'm looking for feedback on onboarding, the endpoint set, and whether the payment flow is too much friction for a utility API.
