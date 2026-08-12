---
title: "Building a Metered Markdown API with Python's Standard Library"
published: false
description: "A factual look at MD2HTML: stdlib HTTP, JSON-backed usage, a free trial, and HTTP 402 payment instructions."
tags: python, api, sideproject, webdev
---

# Building a Metered Markdown API with Python's Standard Library

MD2HTML is a small deployed API for Markdown conversion and related text/HTML utilities. It intentionally avoids a framework: the HTTP layer is Python's `http.server`, state is stored in JSON files, and nginx plus systemd handle the public deployment.

## The real stack

- Python standard library HTTP server
- A small built-in Markdown converter
- JSON/file-backed API-key usage and analytics
- nginx reverse proxy
- systemd service
- Oracle Cloud Always Free ARM VPS

There is no FastAPI, Redis, unique wallet per user, or embedded Litecoin Core node.

## Try the free flow

You can call the API by source IP, or mint an API key without supplying personal information:

```bash
# Optional: mint an independent key
curl http://147.15.103.217/md2html/register

# Convert Markdown; replace mk_... if you chose to register
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: mk_..." \
  -d '{"markdown":"# Hello\n\nThis is **bold**."}'
```

The free trial is 10 billable calls per IP or API key. After exhaustion, billable POST requests return `402 Payment Required` with LTC payment instructions. The current deployment uses a shared payment address; automatic per-user settlement should not be assumed.

## Discover the contract

The service reports version 1.4.0 and 26 product endpoints. Its OpenAPI document is available at:

```text
http://147.15.103.217/md2html/swagger.json
```

Endpoints include conversion, sanitization, batch conversion, Markdown linting, HTML minification, table parsing, JSON formatting, text statistics, slug generation, and webhooks.

## Operational limits

The deployment enforces 30 requests per minute per source IP and a 1 MiB request-body cap. Its public URL is currently HTTP-only, so it is for evaluation and non-sensitive content—not secrets or private documents.

## What I learned

1. A framework is optional for a focused API, but explicit tests and a machine-readable contract are not.
2. Payment copy must describe what is actually automated; vague “wallet balance” claims create a trust failure.
3. A successful copy-paste example matters more than a long feature list.

The API is live at http://147.15.103.217/md2html/. Feedback on the contract and onboarding flow is welcome.
