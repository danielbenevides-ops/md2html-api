# MD2HTML API — Outreach Copy

Pricing: $0.001/call · API base URL: `http://localhost:8777`

---

## 1. Product Hunt Launch

**Title:** MD2HTML API — Markdown to clean HTML in one call

**Tagline:** Fast, simple, $0.001/call markdown-to-HTML conversion API

**Description:**

MD2HTML API turns markdown into clean, semantic HTML with a single POST request. No clutter, no heavy SDKs, no surprises on the invoice — one endpoint, one job, done well.

Send markdown, get back ready-to-render HTML. Perfect forblogs, docs, static site generators, and anywhere you'd rather not ship a full parser. At $0.001 per call, it's cheap enough to sprinkle into pipelines without thinking about cost.

- **Endpoint:** `POST http://localhost:8777`
- **Pricing:** $0.001/call — metered, no monthly fee
- **Use cases:** CMS input sanitization, docs builds, email templates, AI output rendering

Built by a solo developer who got tired of bolting markdown libraries into every side project. One thing, done well.

---

## 2. Hacker News — Show HN

**Title:** Show HN: MD2HTML API — markdown to HTML in one call, $0.001/call

**Body:**

Hey HN — I built a small markdown-to-HTML API after one too many times bolting a parser into a side project. One POST, you get clean semantic HTML back.

- Base URL: `http://localhost:8777`
- Pricing: $0.001/call, metered, no monthly fee
- No auth friction for low-volume use; keys for production

Why a paid API for something libraries do for free? Convenience for pipelines that don't want a parser dependency, and a clean boundary when markdown comes from untrusted input (CMS, user content, AI output). One service owns the surface; everything else downstream consumes HTML.

It's small, honest, and liberally metered. Code isn't open yet, but I'm happy to share the parser internals if anyone wants to nerd out on spec compliance vs. speed. Would love feedback on the pricing model — too cheap to be credible, or refreshingly sane?

---

## 3. Reddit r/webdev — Showoff Saturday

**Body:**

**Showoff Saturday — MD2HTML API**

Built a small API that converts markdown to clean HTML in one call. One endpoint, one job.

- `POST http://localhost:8777`
- $0.001/call, metered — no monthly fee
- Use cases: CMS output, docs builds, AI output rendering, anywhere you don't want to ship a parser

Why: I kept adding markdown libraries to every side project, so I factored it out. It's self-hosted, honest pricing, no upsell tiers.

Not trying to replace GFM or CommonMark parsers in your stack — but if you'd rather have a clean service boundary for untrusted markdown input or shipping docs without a build step, it might fit.

Happy to hear feedback: what would make this worth integrating over keeping your existing parser? What output options would you want (safe mode, xss filtering, custom renderers)?

Sharing because someone asked me last month "how do I just render markdown without 50 dependencies" — figured it might resonate here.

---

## 4. Dev.to Article Outline

**Title:** I Built a $0.001/call Markdown-to-HTML API. Here's Why It's Not As Dumb As It Sounds.

**Section headers:**

1. The problem: every side project gets a markdown parser bolted on
2. What MD2HTML API actually does (one endpoint, clean HTML, metered pricing)
3. Why a service beats a library when markdown is untrusted
4. Pricing at $0.001/call: what that covers and what it signals
5. What's next: open-core parser, self-host option, and feedback I want from you

---
