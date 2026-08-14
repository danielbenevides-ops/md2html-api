# Product Hunt launch pack — MD2HTML API

**Status: BLOCKED — not submitted.** Product Hunt’s web submission page returned Cloudflare HTTP 403, and its GraphQL API returned HTTP 401 (`invalid_oauth_token`). No Product Hunt account/session or API token is available in this environment. Do not claim a listing without a URL.

## Exact listing copy

- **Name:** MD2HTML API
- **Tagline:** Markdown to HTML over HTTP; 10 free calls, then LTC
- **Product URL:** https://147.15.103.217.sslip.io/md2html/
- **Source URL:** https://github.com/danielbenevides-ops/md2html-api
- **Topics:** Developer Tools, APIs, Open Source, Markdown, Crypto
- **Description:** Convert Markdown to HTML with one HTTP request. No signup or SDK: send JSON, receive rendered HTML. The live API includes a 10-call free tier; after that it is **0.001 LTC per 100 calls in Litecoin (LTC)**, with a 30-requests-per-minute IP limit. Open source and self-hostable.

## Exact maker comment

Hey Product Hunt 👋 I built MD2HTML to make Markdown rendering a boring HTTP call instead of another SDK or dependency. Send JSON, get HTML back, and try 10 calls free with no signup. After the free tier, usage is **0.001 LTC per 100 calls in Litecoin (LTC)**—no subscription. The API and source are public. What would make a tiny Markdown API useful in your stack: more syntax, SDKs, or webhooks?

## Assets / sources

- Ready factual launch copy: `posts/hn_showhn_final.md`
- Ready story, curl, and pricing copy: `blog/why-we-built-free-markdown-api.md`
- Live preflight observed: `/health` returned `status: ok`, version `1.5.0`; `/pricing` reported 10 free calls and `$0.001`/call in LTC.
- **Thumbnail:** not present under `posts/` or `blog/`; create a 1270×760 image reading “MD2HTML API — Markdown in → HTML out — 0.001 LTC per 100 calls”.
- **Gallery:** capture `/docs`, a successful `/convert` JSON response, and a curl example. No image files are currently present under `posts/` or `blog/`.
- Do not reuse stale pricing claims in `posts/indiehackers_final.md`; use the live `/pricing` response.

## Current official submission attempt — blocked

- Requested official flow: `https://www.producthunt.com/posts/new`.
- Live request result: **HTTP 403 Forbidden** with `Cf-Mitigated: challenge` and `Server: cloudflare`; the response is Cloudflare’s “Just a moment...” challenge requiring JavaScript and cookies.
- No Product Hunt account/session or OAuth token is available, so no challenge bypass or unauthenticated submission was attempted. **No Product Hunt listing URL exists.**
- Accountless directory action identified (not submitted): use the **1000 Tools** single submission form. The SubmitSaaS no-login directory page describes it as “Form only, no account” and “Single-form submission; no account to create or manage.” Verify the destination form before sending.
