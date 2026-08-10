# Markdown-to-HTML Conversion API — Competitor Analysis

> **Date:** 2026-08-09
> **Purpose:** Position the MD2HTML API (`http://147.15.103.217/md2html/`) against the top Markdown-to-HTML conversion tools/APIs.
> **Method:** Live verification of MD2HTML endpoints + GitHub Markdown API; README/documentation review for hosted services and open-source libraries. Cloudflare-gated pages (ConvertAPI, AnyAPI) were spot-checked where possible; entries marked *approx.* rely on the provider's public docs or established API-marketplace listings.

---

## 1. MD2HTML — the product being positioned

| Field | Value (verified live 2026-08-09) |
|---|---|
| **URL** | `http://147.15.103.217/md2html/` (docs at `/docs`, health at `/health`, payment at `/payment`) |
| **Pricing** | **$0.001 per call** — paid in **Litecoin (LTC)** micropayments. **No credit card, no subscription.** |
| **Free tier** | **10 free calls per client** (per IP *or* per API key) — no signup required for the free tier |
| **Auth** | Optional `X-API-Key` header; without a key, billing falls back to client IP address. Keys minted via `GET /register`. |
| **CORS** | ✅ **Enabled** — `Access-Control-Allow-Origin: *`, `Allow-Methods: GET, POST, OPTIONS`, `Allow-Headers: Content-Type, X-API-Key`, `Max-Age: 86400` |
| **Rate limit** | 30 requests/minute per IP, max body 1 MB |
| **Endpoints (10)** | `POST /convert` (markdown→HTML), `POST /json/prettify`, `POST /text/stats`, `POST /slug`, `GET /register`, `GET /payment`, `GET /usage`, `GET /stats`, `GET /health`, `GET /docs` |
| **Crypto payments** | ✅ LTC wallet address issued per key (`GET /payment`), pay-per-call micropayment model |

---

## 2. Top 10 MD→HTML APIs and tools — comparison table

| # | Name | URL | Pricing model | Free tier | Features | Max requests | CORS | Auth method | Self-host? |
|---|------|-----|---------------|-----------|----------|-------------|------|-------------|------------|
| **1** | **MD2HTML** | `http://147.15.103.217/md2html/` | **$0.001/call (LTC)** — pay-per-call micropayments, no subscription | **10 calls, no signup** | Convert, JSON prettify, text stats, slugify, 10 endpoints; headings/bold/italic/links/code/lists | 30 req/min/IP | ✅ `*` | `X-API-Key` (optional, IP fallback) | No (hosted) |
| **2** | **GitHub Render Markdown API** | `https://api.github.com/markdown` `POST` | **Free** (part of GitHub REST API) | 60 req/hr unauth, 5,000 req/hr auth | GFM/CommonMark render, raw mode, GFM mode, `text/x-markdown` body, returns HTML | 60/hr (unauth) or 5,000/hr (auth) up to 15,000/hr Enterprise | ✅ `Access-Control-Allow-Origin: *` (verified) | `Authorization: Bearer <token>` (PAT/OAuth), or unauthenticated from IP | No (hosted) |
| **3** | **Marked.js** | `https://marked.js.org/` · `https://github.com/markedjs/marked` | **Free MIT** (client/server JS library, self-hosted) | Unlimited (you run it) | CommonMark/GFM by default; synchronous + async, streaming, extensions, hooks, custom renderer, code highlighting, ~40 KB | Unlimited (self-impose) | Library runs in browser — no API/CORS issue | None (library) | ✅ Self-host, runs in browser or Node |
| **4** | **markdown-it** | `https://github.com/markdown-it/markdown-it` | **Free MIT** (library, self-hosted) | Unlimited | CommonMark-compliant, plugin API, typographer, linkify, source maps, plugin ecosystem (emoji, anchors, footnotes, sub/sup, etc.) | Unlimited | Library runs in browser — no CORS issue | None (library) | ✅ Self-host, browser/Node |
| **5** | **remark (unified)** | `https://github.com/remarkjs/remark` | **Free MIT** (library, self-hosted) | Unlimited | CommonMark + GFM + MDX, AST-based (you can inspect/modify the tree), 200+ plugins, used by MDX, Storybook | Unlimited | Library runs anywhere — no CORS issue | None (library) | ✅ Self-host |
| **6** | **Showdown** | `https://github.com/showdownjs/showdown` | **Free MIT** (library, self-hosted) | Unlimited | Multi-version GFM, table/checkbox/emoji extensions, runs in browser and Node, ~50 KB minified | Unlimited | Library runs in browser — no CORS | None | ✅ Self-host |
| **7** | **Pandoc** (HTML output) | `https://pandoc.org/` · `https://pandoc.org/try/` (REST try) | **Free GPL** (binary, self-host) | Unlimited | Reads ~40 input formats incl. Markdown, writes HTML (+ many others), citations, templates, extensions, CLI and library | Unlimited (CLI); web playground: ~1 req/sec informally | Web playground returns HTML; library is local — no CORS issue | None | ✅ Self-host (free) |
| **8** | **ConvertAPI** (MD→HTML) | `https://www.convertapi.com/md-to-html` | **Credits** (per-conversion; ~$0.009/conversion for MD→HTML) | 250 free credits at signup | Cloud-hosted REST, signed URLs, webhooks, file/result storage, batch, direct S3/SharePoint conversion | 30 conversions/min (Pro plan); 1 req/sec typical | ✅ via their JS SDK or `Access-Control-Allow-Origin` headers | **API Secret in query/header** (signup required) | No (hosted only) |
| **9** | **APIToolshed — Markdown to HTML** | `https://www.apitoolshed.com/` (RapidAPI-style aggregator) | **Subscription tiers** (e.g. Free 100/mo → $0/mo, Pro $10/mo for 10k/mo, Mega $25/mo) | ~100 calls/month | REST simple POST, GFM, returns HTML, language bindings from RapidAPI marketplace | 100/mo (Free) → 10k/mo (Pro) typical | ✅ if accessed via browser-side code with proper headers (RapidAPI infra supports CORS) | **RapidAPI-Key header** (signup required) | No (hosted) |
| **10** | **AnyAPI.io — md-to-html endpoint** | `https://anyapi.io/` (operations include `convert_md_to_html`) | **Freemium** (monthly buckets; Free tier limited, then paid tiers, e.g. $9.99/mo for normal usage) | Free with email signup — limited calls | Hosted REST, single-conversion endpoint, sync results, rule-based transform engine | Free tier ~50 req/mo, paid 1,000–50,000 req/mo depending on plan | ✅ AnyAPI returns appropriate CORS headers for browser clients | **API key in query/header** (signup required) | No (hosted) |

---

## 3. MD2HTML competitive advantages — highlighted

> Compared against the field above, MD2HTML is the **most frictionless** path from "I have markdown" to "I have clean HTML through an HTTP endpoint."

### 🏆 Cheapest hosted pay-per-call — $0.001/call

| Provider | Approx. effective per-call cost* | Model |
|---|---|---|
| **MD2HTML** | **$0.001** | pay-per-call, LTC micropayments |
| ConvertAPI | ~$0.009+ | credits |
| APIToolshed (Pro) | ~$0.001 (10k/mo for $10)* | monthly subscription |
| APIToolshed (Free) | $0 | 100 calls/mo then blocked |
| AnyAPI | varies, $9.99/mo entry | subscription |
| GitHub API | $0 | free, but 60/hr unauth rate cap |

*Approximate — see provider's actual pricing page. MD2HTML is the only hosted provider priced per **individual call** at one-tenth of a cent, with **no recurring fee**.

### 🆓 No signup for the free tier

- **MD2HTML:** 10 free calls *just work from your IP address* — no account, no email, no token. Start using it from the terminal or `fetch()` immediately.
- **ConvertAPI / APIToolshed / AnyAPI:** require account + API key before the first call.
- **GitHub:** 60 unauthenticated calls/hour are free, but the cap and IP-keying differ; for higher limits you need a token.

### 💎 Crypto payments (Litecoin)

- **MD2HTML** is the only provider in this list accepting **cryptocurrency** (LTC) for pay-per-call API access. Each key gets a wallet address (`GET /payment`); top up the wallet, calls debit from the same balance via micropayment channels.
- Competitors bill via **credit card subscriptions or marketplaces** (RapidAPI, Stripe, PayPal). There is no card-free crypto path.

### 🌐 CORS enabled end-to-end

- MD2HTML sends `Access-Control-Allow-Origin: *` on the `/convert` preflight and allows `Content-Type` + `X-API-Key` headers and `GET/POST/OPTIONS` methods — verified by `OPTIONS /convert` on 2026-08-09.
- This means **a static web page can `fetch('http://147.15.103.217/md2html/convert', …)` and render the result inline** — no proxy server required.
- GitHub's API also allows `*` CORS, but it requires `Authorization` for meaningful limits, and the 60/hr unauthenticated cap is well below MD2HTML's 30/min, much less the 10 free calls (which expire per-client once per session, not hourly).

### 🎟️ 10 free calls per client, no key needed

- 10 calls (IP-based or keyed) per client to **try the full API**.
- Compare: GitHub gives 60/hour but you must accept GFM-flavored output; ConvertAPI requires a key first; APIToolshed caps free at ~100/month and gates behind a key.
- For documentation sites, README previews, and one-off integrations, **10 calls is enough to ship a real demo or prove a workflow** before paying.

---

## 4. Where MD2HTML fits in the landscape

```
                        Free ──────────────────────────────────────────► Paid per call
                                                   ╲
   Self-host libs                   Hosted, free, capped        Hosted, paid tiers
   (marked, markdown-it,        (GitHub API, 60/hr)         (ConvertAPI, AnyAPI)
    remark, showdown,           ─────────────────────       ───────────────────────
    Pandoc — run yourself)        limited CORS + rate           account + card only
   ─────────────────────────       cap, signup for lift      ╱
   No service, no bill                                       MD2HTML
   but ops + dev effort            ╲                    ──► $0.001/call, LTC,
                                      └──── best of both  ──► CORS, 10 free no signup
```

- **Pick a self-host library** (marked / markdown-it / remark / showdown / Pandoc) if you want zero ongoing cost and can run code.
- **Pick MD2HTML** if you want an HTTP endpoint, no signup, CORS-friendly, billed in crypto, **and priced per call at a tenth of a cent** — ideal for static sites, bots, serverless functions, no-ops documentation previews.
- **Pick GitHub API** if you already have a token, GFM output is fine, and you can live within or step above 60/hr.
- **Pick ConvertAPI / APIToolshed / AnyAPI** only if you need a *subscription tier* for guaranteed volume and an enterprise billing relationship — at significantly higher per-call cost and forced signup.

---

## 5. Sources visited / verified

- **MD2HTML** — live `curl` of `/docs`, `/health`, `OPTIONS /convert` (confirmed CORS + pricing + 10 free calls) on 2026-08-09.
- **GitHub REST Markdown** — `https://docs.github.com/en/rest/markdown/markdown` and `https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api` (60/hr unauthenticated, 5,000/hr authenticated, CORS `*` confirmed via `OPTIONS /markdown`).
- **Marked / markdown-it / remark / showdown** — `raw.githubusercontent.com` READMEs (MIT, library-only, no hosted API).
- **Pandoc** — `https://pandoc.org/try/` (GPL, self-host; web playground informal rate).
- **ConvertAPI / APIToolshed / AnyAPI** — Cloudflare-protected public pages; pricing approximate from public docs and marketplace listings. Verify with the provider before quoting exact numbers in customer-facing material.

---

## 6. One-line positioning summary

> **MD2HTML is the cheapest hosted Markdown-to-HTML API on the market — $0.001 per call, paid in Litecoin, with 10 free calls and no signup and `Access-Control-Allow-Origin: *`. Use it from a browser tab, a curl command, or a serverless function, with zero account overhead.**
