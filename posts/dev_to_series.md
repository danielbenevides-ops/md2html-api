---
title: "Building MD2HTML API with AI — A 5-Part Dev.to Series"
series: buildmd-with-ai
status: draft
---

# 🛠️ Building MD2HTML API with AI: A 5-Part Dev.to Series

### *From $0 to $1 MRR — shipping a pay-per-call Markdown API in public*

This series documents the full journey of building **MD2HTML API** — a 10-endpoint Markdown processing service with crypto payments, rate limiting, and API-key auth — using AI-assisted development throughout. Live at `https://147.15.103.217.sslip.io/md2html/`.

**Target audience:** Indie hackers, side-project builders, and developers curious about shipping a real paid API with modern tooling.

**Cross-posted to:** Dev.to (canonical), personal blog via MD2HTML API (eat your own dogfood).

---

## Part 1 — The Idea

### Title: "MD2HTML API Part 1: The Idea — Turning Markdown Into a Pay-Per-Call API"

**Summary:** Every content pipeline reinvents Markdown→HTML conversion — blog engines, static site generators, docs sites, newsletter tools — so why not ship it as a clean paid API and stop the wheel-reinvention? This post unpacks the core insight (Markdown-to-HTML is a wrapped commodity that nobody wants to self-host), defines the product scope (10 endpoints covering conversion, syntax highlighting, TOC generation, sanitized output), and sets the revenue goal that grounds the entire series: **$1 MRR first, growth later**. The idea isn't to build a billion-dollar company — it's to prove one developer with AI can ship a real, revenue-generating API in public.

**Key code snippet:**

```python
# Core API contract — one decorator, ten endpoints
from fastapi import FastAPI, Request, HTTPException
import mistune

app = FastAPI(title="MD2HTML API", version="1.0")

API_KEYS = {"sk_live_xxx": {"plan": "free", "quota": 100}}

def require_key(func):
    async def wrapper(request: Request, *args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if key not in API_KEYS:
            raise HTTPException(401, "Invalid or missing API key")
        return await func(request, *args, **kwargs)
    return wrapper

@app.post("/v1/convert")
@require_key
async def convert(request: Request):
    body = await request.json()
    md = body.get("markdown", "")
    html = mistune.html(md)  # 10 endpoints all wrap this pipeline
    return {"html": html, "input_chars": len(md), "output_chars": len(html)}
```

**Status:** Ready to publish
**Cover image prompt:** A single highlighted `#` Markdown heading morphing into a glowing `<h1>` HTML tag, warm orange-to-teal gradient, isometric, dev.to style.
**Tags:** `#productivity #indiehackers #webdev #ai`

---

## Part 2 — The Stack

### Title: "MD2HTML API Part 2: The Stack — FastAPI + Postgres + Redis (and an AI Co-pilot)"

**Summary:** Part 2 walks through the production stack chosen for speed and low operating cost: Python FastAPI for the 10 endpoints, PostgreSQL for API keys and usage ledgering, Redis for rate-limit counters and response caching, and Caddy for automatic HTTPS reverse proxy on a single $5 VPS. Every layer was selected or validated with an AI co-pilot that helped write the initial boilerplate, design the migration files, and generate the Docker Compose configuration — drastically cutting time-to-first-deploy. The post also shares the tuning decisions (sync vs async DB driver, `gunicorn -k uvicorn.workers.UvicornWorker`, connection pool sizing) that actually mattered under load.

**Key code snippet:**

```python
# Database-backed rate limiter — Redis sliding window
async def check_rate_limit(api_key: str, limit: int = 100, window: int = 3600):
    pipe = redis.pipeline()
    key = f"rl:{api_key}:{int(time.time() // window)}"
    pipe.incr(key).expire(key, window)
    count, _ = pipe.execute()
    if count > limit:
        raise HTTPException(429, detail=f"Rate limit exceeded: {count}/{limit}")
    return count  # for the X-RateLimit-Remaining header

# Used by the same @require_key decorator from Part 1
# — limits are plan-based: free=100/hr, pro=1000/hr, enterprise=unlimited
```

**Status:** Ready to publish
**Cover image prompt:** A stacked isometric diagram: FastAPI → Postgres → Redis → Caddy → VPS, translucent layers with arrows, cool blue palette.
**Tags:** `#python #fastapi #webdev #indiehackers`

---

## Part 3 — Crypto Payments

### Title: "MD2HTML API Part 3: Crypto Payments — X402 and the Magic of Pay-Per-Call"

**Summary:** Part 3 explains how MD2HTML API accepts crypto payments via the `X402` coinbase Commerce protocol, letting users top up their API key balance without a credit card, KYC, or a Stripe account — frictionless onboarding that's ideal for international and privacy-conscious developers. It covers the payment flow end-to-end: user initiates `POST /v1/billing/topup` → receives a Coinbase Commerce checkout URL → pays in BTC/ETH/USDC → webhook hits `POST /v1/billing/webhook` to credit the balance. Control stays in our hands — no payment processor blocks revenue or freezes payouts.

**Key code snippet:**

```python
# X402 pay-per-call:path → Coinbase checkout → webhook credits balance
@app.post("/v1/billing/topup")
async def create_charge(amount_usd: float = 0.50):
    charge = coinbase_client.create_charge(
        name=f"MD2HTML TopUp ${amount_usd:.2f}",
        pricing_type="fixed_price",
        local_price={"amount": str(amount_usd), "currency": "USD"},
    )
    return {"checkout_url": charge["hosted_url"], "code": charge["code"]}

@app.put("/v1/billing/webhook")
async def webhook(payload: dict, x_cc_webhook_signature: str = Header(...)):
    # Verify HMAC signature, confirm confirmed@type charge against: amount
    event = verify_signature(payload, x_cc_webhook_signature)
    api_key = event["metadata"]["api_key"]
    # Credit balance atomically — idempotent on charge code
    await db.execute(
        "UPDATE balances SET remaining = remaining + $1 WHERE api_key = $2",
        Decimal(str(event["pricing"]["local"]["amount"])), api_key)
    return {"status": "ok"}
```

**Status:** Ready to publish
**Cover image prompt:** A crypto coin sliding into a glowing API endpoint, dark background, laser blue accents.
**Tags:** `#crypto #payments #webdev #indiehackers`

---

## Part 4 — Security Hardening

### Title: "MD2HTML API Part 4: Security Hardening — Keeping a Paid API Online and Not Getting Owned"

**Summary:** Part 4 drops into the unglamorous security work that keeps a public paid API from becoming someone's free compute pipeline or an XSS vector: API-key hashing with SHA-256, key rotation endpoints, CORS strict-origin policy, HTML output sanitization with `bleach`, and input size limits to prevent megabyte Markdown bombs. It also covers the operational layer — Caddy `iptables` rate limiting per IP, a fail2ban-style ban after repeated 401s, Sentry error capture, and daily DB backups off the VPS. The takeaway is clear: security isn't a single feature, it's a stack of small annoying layers that together stop 99% of abuse before it costs you a $20 VPS bill or a Trustpilot review.

**Key code snippet:**

```python
# Output sanitization — no XSS from your Markdown API
import bleach

ALLOWED_TAGS = ['p','h1','h2','h3','strong','em','a','ul','ol','li',
                'blockquote','code','pre','hr','br','span','div','table',
                'thead','tbody','tr','th','td']
ALLOWED_ATTRS = {'a': ['href','title'], 'span': ['class']}

def sanitize(html: str) -> str:
    # bleach.clean strips unknown tags/attrs, keeps a safe subset
    safe = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS,
                        protocols=['https'], strip=True)
    return safe

# Input guard — reject Markdown payloads > 500 KB
MAX_INPUT = 500 * 1024  # ~500KB

@app.post("/v1/convert")
async def convert(request: Request, body: dict):
    md = body.get("markdown", "")
    if len(md.encode()) > MAX_INPUT:
        raise HTTPException(413, f"Markdown too large (max {MAX_INPUT//1024}KB)")
    html = sanitize(mistune.html(md))
    return {"html": html}
```

**Status:** Ready to publish
**Cover image prompt:** A shield icon wrapping an API endpoint, padlock and key, dark navy, neon green accents.
**Tags:** `#security #webdev #python #indiehackers`

---

## Part 5 — Distribution

### Title: "MD2HTML API Part 5: Distribution — How (and Where) to Actually Get Users for Your API"

**Summary:** Part 5 is the honest truth nobody tells you: building the API was the easy part — getting the first paying user is where most side projects die. It covers the distribution playbook that landed MD2HTML its **$1 MRR**: canonical blog posts cross-posted to Dev.to, Hacker News, and Indie Hackers; SEO-optimized playground pages (one per endpoint; Markdown → Live HTML), so Google sends organic traffic; a free tier with visible usage meters so users hit the upgrade wall naturally; and a public roadmap that turns users into co-designers. The revenue-first mindset throughout: optimize for that first paid call, not for scale, and let each new user teach you what to build next.

**Key code snippet:**

```python
# SEO landing pages — one route per endpoint, auto-generated swagger docs
PAGES = {
    "/mardown-to-html": "Convert Markdown to sanitized, ready-to-render HTML.",
    "/markdown-to-toc": "Generate a table of contents from Markdown headings.",
    "/markdown-syntax-highlight": "Add Pygments syntax highlighting to code blocks.",
    "/markdown-stripped": "Strip all formatting — Markdown to plaintext in one call.",
    # ... 10 public-facing pages, one per endpoint
}

@app.get("/try/{slug}")
async def playground(slug: str, request: Request):
    desc = PAGES.get(slug, "Try the MD2HTML API — free tier included.")
    # Server-renders an interactive demo page (calls the API itself)
    return HTMLResponse(render_template("try.html", slug=slug, desc=desc,
        headless_url="https://md2html.api.buildmd.io"))
```

**Status:** Ready to publish
**Cover image prompt:** A megaphone broadcasting API endpoints into a crowd of browser windows, warm gradient, dev.to style.
**Tags:** `#distribution #marketing #indiehackers #webdev`

---

## Series Prep — Dev.to Setup Checklist

- [ ] Create canonical blog post on MD2HTML blog (built via the API itself — meta power move)
- [ ] Cross-post each part to Dev.to with `canonical_url` set to the blog original (avoids duplicate-content SEO penalty on Dev.to)
- [ ] Add series cover image 1200×675, generated via Flux or hand-designed in Figma
- [ ] End each part with a "Next in this series" link to the next published article
- [ ] Include call-to-action: "MD2HTML API is live at https://147.15.103.217.sslip.io/md2html/ — first 100 calls free"
- [ ] Drop GitHub stars link: github.com/pqcai/md2html-api
- [ ] Add embedded API playground widget on the Dev.to posts (using the markdown → HTML endpoint itself)
- [ ] Set Dev.to tags exactly as listed above to match Dev.to tag taxonomy
- [ ] Pub schedule: 1 part per week for 5 consecutive Tuesdays at 14:00 UTC
- [ ] After Part 5 publishes, bundle the whole series as a downloadable PDF guide (via the API, natch)

---

## Promotion Plan

| When | Platform | Action |
|------|----------|--------|
| Part 1 publish | Hacker News | "Show HN: I built a paid MD2HTML API with AI" |
| Part 1 publish | Indie Hackers | Cross-link the Indie Hackers community post |
| Part 3 publish | r/CryptoCurrency | "How I added crypto payments to a side-project API without a bank account" |
| Part 4 publish | r/NetSec | Security-focused distribution angle |
| Part 5 publish | Twitter/X | Thread version of the entire series, with revenue numbers |

---

*This series outline is a living document — update each part's status and notes as drafts are written and edited.*
