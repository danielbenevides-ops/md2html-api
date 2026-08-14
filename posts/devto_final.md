---
title: "A curl-Friendly Markdown-to-HTML API"
published: false
description: "A factual walkthrough of MD2HTML API: Markdown conversion and related developer utilities over HTTP."
tags: api, python, devtools, opensource
canonical_url: ""
cover_image: ""
---

# A curl-Friendly Markdown-to-HTML API

MD2HTML API is an HTTP service for converting Markdown to HTML and running related developer utilities. The public source is on GitHub, and the live service is available at:

- **API:** <https://147.15.103.217.sslip.io/md2html/>
- **Repository:** <https://github.com/danielbenevides-ops/md2html-api>

This is a project description and usage guide—not a claim about customer adoption, uptime guarantees, or performance benchmarks.

## Quick start

The conversion endpoint accepts JSON. A basic request is:

```bash
curl -X POST https://147.15.103.217.sslip.io/md2html/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello **world**\n\n- one\n- two"}'
```

The endpoint returns JSON. A successful conversion includes an `html` field and billing metadata; counters and availability depend on the client and the current service state.

At verification, `GET /health` returned HTTP 200 with `{"status":"ok"}` and version `1.5.0`. Conversion access is subject to the per-client free tier and rate limit, so this point-in-time check is not an uptime or availability guarantee.

## What is available

The current `/health` response advertises 26 routes. Among them are:

- `GET /register` and `/keys/info` — API-key registration and usage information
- `POST /convert` — Markdown to HTML
- `POST /markdown/lint` — report Markdown syntax warnings
- `POST /html/minify` and `/table/parse` — content utilities
- `POST /sanitize` — sanitize Markdown input
- `POST /batch` — convert multiple Markdown strings
- `POST /minify` — minify HTML, CSS, or JavaScript
- `POST /html/extract` — extract visible text from HTML
- `POST /url/shorten` — create a short code for a URL
- `POST /cron/parse` — describe a five-field cron expression
- `POST /regex/test` — test a regular expression
- `POST /json/prettify` — format a JSON document
- `POST /text/stats` — calculate text statistics
- `POST /slug` — generate a URL-safe slug

There are also public `GET` routes for health, documentation, pricing, payment instructions, usage, and aggregate statistics. Check `/docs` for the request formats rather than relying on an old snippet.

## Pricing and limits

At the time of verification, the live `/pricing` endpoint reported 10 free calls per client (identified by IP or `X-API-Key`), followed by a listed price of `$0.001` per call in LTC. It also reported a 30-request-per-minute IP rate limit and a 1 MiB maximum request body. These are published service terms—not evidence that a payment was sent, verified, or credited—so the live API response remains authoritative.

## Run it yourself

The reference repository documents Python 3.8+ and a Python-standard-library-only runtime:

```bash
git clone https://github.com/danielbenevides-ops/md2html-api.git
cd md2html-api
python server.py
```

For a local instance, the server listens on port `8777` according to the project documentation. This describes the reference implementation, not the hosted service's deployment topology, redundancy, or SLA. Review the repository's deployment and security notes before exposing a self-hosted instance to the internet.

## Why this is useful

For a script, CI job, documentation pipeline, or small internal tool, an HTTP boundary can be convenient: the caller only needs to send JSON and handle JSON. The repository is MIT-licensed, so you can inspect the implementation, self-host it, or adapt it to your own workflow.

No third-party quotes or adoption figures are included because they are not needed to try the API. If you use it, evaluate the output and the repository for yourself.

**Live API:** <https://147.15.103.217.sslip.io/md2html/>
**Source:** <https://github.com/danielbenevides-ops/md2html-api>
