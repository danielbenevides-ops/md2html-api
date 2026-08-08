# Market Research v3 — MD2HTML API: 5 Developer Use Cases That Pay

> Markdown-to-HTML API · $0.001/call · LTC crypto-native · zero-signup
> Live: http://147.15.103.217/md2html/ · OSS: github.com/dcn13l/md2html-api
> Compiled 2026-08-08 · Supersedes v2 (productizes findings into 5 sellable use cases)
> Method: primary-source — npm download counts (api.npmjs.org), GitHub repo search (api.github.com), Stack Overflow (api.stackexchange.com), OpenAI community + Ghost developer forums.

---

## 1. AI Output Rendering Pipelines (ChatGPT/LLM-chatbot wrappers)

**Target user:** Devs building ChatGPT/DeepSeek/Claude-style chatbot front-ends, AI agent dashboards.
**Problem:** LLMs emit markdown (tables, code, links); the UI must render to HTML. `react-markdown` does this client-side — npm hits **30M/week** — but is one more bundled dep with dialect drift. Server-hosted `marked` (62M/wk) needs security-patch maintenance.
**How MD2HTML solves it:** Single POST → `{markdown, html}` JSON. One render layer across LLM dialects. No client bundling. 10 free calls cover PoC integration.
**Willingness to pay:** $50/mo (early wrapper) → $1k+/mo (production pipeline, 100k+ calls). Wrapper apps confirm this is the integration devs self-host.

## 2. Notion-like Editor HTML Preview / Rich-text Export

**Target user:** Builders of note apps, knowledge-base SaaS, "Notion-like" tools.
**Problem:** Validated pain on Ghost dev forum — engineers maintain markdown→Mobiledoc/AST/HTML preprocessing, fighting the post-edit render. ConvertAPI and Aspose ($19+/mo) both demand signup/card before first test.
**How MD2HTML solves it:** Server-side HTML render from the editor's markdown buffer; preview pane fetches HTML without bundling a JS renderer per session. Crypto billing → vendor never front-loads a card.
**Willingness to pay:** $100–500/mo per SaaS (10k–100k renders/mo).

## 3. Static Site Generator Plugins (11ty / Hugo / Jekyll)

**Target user:** SSG plugin authors; solo-blog owners without JS build pipelines.
**Problem:** GitHub repo search surfaced static-site markdown plugins (markata 93★, netlify-plugin-ghost-markdown 69★). Each plugin reinvents Marked/remark plumbing per SSG. GitHub's free Markdown API caps at 60/hr unauth — breaks first real build.
**How MD2HTML solves it:** One endpoint as a renderer step — same HTML across every SSG, no native deps. Zero-signup suits plugin users; crypto lets plugins resell without their own billing.
**Willingness to pay:** Plugin author $10–50/mo (low-volume). Plugin-of-record can resell MD2HTML under a per-call crypto-flow royalty.

## 4. Headless CMS / Blog-Platform Markdown Rendering

**Target user:** Backend engineers at Ghost/Strapi/Decap clones; comment/forum software rendering MD server-side.
**Problem:** Self-hosting Marked.js is a security-patch treadmill; GitHub/GitLab APIs are rate-capped (60/hr / ~600/min), capping preview+publish traffic.
**How MD2HTML solves it:** Server-side render, clean JSON contract, no lib to maintain, no rate-limit wall. Per-call pricing scales with user growth.
**Willingness to pay:** $100–1,000/mo at scale (100k–1M renders/mo) — v2 Persona A, highest LTV.

## 5. API Documentation / README Rendering

**Target user:** DevRel teams, OSS maintainers, internal docs sites rendering README → HTML.
**Problem:** GitHub's 300M+ READMEs prove markdown is the default docs format. But its API ToS blocks commercial resale; Stack Overflow questions about target=_blank (845 votes), cross-refs (766), image sizing (496) show devs need controlled HTML GitHub won't give them.
**How MD2HTML solves it:** Docs pipeline calls MD2HTML per file/preview-deploy; commercial-resale rights honored (OSS, self-hostable). Predictable HTML hooks for SEO/CSS.
**Willingness to pay:** $30–100/mo (indie docs) → $500+/mo (enterprise DevRel pipeline).

---

**Cross-cut pricing win:** MD2HTML's $0.001/call floor sits below the card-processing floor ($0.30 + 2.9%) — card-billed competitors cannot match it, locking a defensible crypto-micropayment niche across all 5 use cases.
