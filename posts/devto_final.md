---
title: "A Dependency-Free Markdown-to-HTML API You Can Call with curl"
published: false
description: "A factual walkthrough of MD2HTML API: Markdown conversion and small developer utilities over HTTP."
tags: api, python, devtools, opensource
canonical_url: ""
cover_image: ""
---

# A Dependency-Free Markdown-to-HTML API You Can Call with `curl`

MD2HTML API is a small HTTP service for converting Markdown to HTML and running a few related developer utilities. The public source is on GitHub, and the live service is available at:

- **API:** <http://147.15.103.217/md2html/>
- **Repository:** <https://github.com/dcn13l/md2html-api>

This is a project description and usage guide—not a claim about customer adoption, uptime guarantees, or performance benchmarks.

## Quick start

The conversion endpoint accepts JSON. A basic request is:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello **world**\n\n- one\n- two"}'
```

The response is JSON with an `html` field and billing metadata. The exact counters depend on the client making the request.

A live check performed while preparing this article returned HTTP 200 from `/convert` and an HTML result for Markdown input. The health endpoint also returned `{"status":"ok"}` and reported release version `1.3.0` at that moment. Those are point-in-time observations, not a promise that the service will always be available.

## What is available

The live `/health` response currently lists these routes:

- `POST /convert` — Markdown to HTML
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

At the time of verification, the live `/pricing` endpoint reported a 10-call free tier, followed by a listed price of `$0.001` per call in LTC. It also reported a 30-request-per-minute IP rate limit and a 1 MiB maximum request body. Limits and pricing can change, so the API response is the authoritative reference.

## Run it yourself

The repository documents Python 3.8+ and no third-party runtime dependencies:

```bash
git clone https://github.com/dcn13l/md2html-api.git
cd md2html-api
python server.py
```

For a local instance, the server listens on port `8777` according to the project documentation. Review the repository's deployment and security notes before exposing a self-hosted instance to the internet.

## Why this is useful

For a script, CI job, documentation pipeline, or small internal tool, an HTTP boundary can be convenient: the caller only needs to send JSON and handle JSON. The repository is MIT-licensed, so you can inspect the implementation, self-host it, or adapt it to your own workflow.

No third-party quotes or adoption figures are included because they are not needed to try the API. If you use it, evaluate the output and the repository for yourself.

**Live API:** <http://147.15.103.217/md2html/>  
**Source:** <https://github.com/dcn13l/md2html-api>
