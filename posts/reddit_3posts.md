# Reddit Posts — MD2HTML API

> 3 posts, each under 250 words, authentic tone. Live URL: http://147.15.103.217/md2html/ · GitHub: https://github.com/danielbenevides-ops/md2html-api

---

## Post 1 — r/webdev (Showoff Saturday)

**Title:** Built a Markdown-to-HTML API that costs 0.001 LTC per 100 calls

**Body:**

Been meaning to share this in the Saturday thread. I built **MD2HTML** — a REST API that takes raw Markdown and returns clean, styled HTML. One endpoint, no SDK, no signupwall.

```
POST http://147.15.103.217/md2html/convert
Body: your markdown → response: HTML
```

The angle that got me actually building it: existing converters are either paid per month, rate-limited to uselessness, or want you to install a whole markdown lib. I wanted a single curl call. 10 free calls, then 0.001 LTC per 100 calls — and the billing is Litecoin micropayments, not a card. No Stripe account, no KYC, deposit a few cents of LTC and you're calling forever.

Stack is deliberately unsexy: Python stdlib `http.server`, no Flask/FastAPI, no database, file-based ledger. The whole thing is a few hundred lines and deploys with one SSH command. 10 endpoints total (convert, health, balance, deposit address, docs, etc.).

It's live right now: **http://147.15.103.217/md2html/** — there's a playground on the docs page so you can try it without committing.

Source is open: **https://github.com/danielbenevides-ops/md2html-api**

What I'd genuinely like feedback on: is the deposit-LTC-then-call flow acceptable for something this cheap, or is that a dealbreaker vs. a card on file? I suspect per-call sub-cent pricing only makes sense if the payment side is also frictionless, and I'm not sure LTC is there yet. Roast the API design too if you want — rate limiting and caching are still TODO.

---

## Post 2 — r/selfhosted

**Title:** Self-hostable markdown conversion API with crypto micropayments

**Body:**

Working on a small self-hostable service called **MD2HTML** and looking for input, since most of you run your own infra.

It's a REST API: Markdown in, clean HTML out. The interesting bit is the billing — pay-per-call at $0.001/request in Litecoin, no Stripe, no accounts. If you're already self-hosting, you don't want a SaaS subscription to render markdown. But you might host this yourself and either eat the cost or let users drop sats into a deposit address.

Why it fits here:

- **No deps.** Python stdlib `http.server`. No 500MB Docker image, no node_modules. `git clone` and run.
- **No database.** Balance ledger is a JSON file — back it up with rsync like everything else.
- **It's yours.** You control the wallet keys, logging, rate limits. Run it beside your docs site.
- 10 endpoints, few hundred lines, one SSH deploy.

Live demo: **http://147.15.103.217/md2html/**
Self-host it: **https://github.com/danielbenevides-ops/md2html-api**

Questions for the room:
1. Does the LTC layer add value on a self-hosted tool, or is it overkill when you can just disable billing?
2. Anyone doing per-call crypto billing on self-hosted services? What wallet/library did you land on — I'm on LiteWallet, fine but not amazing.
3. Anything in the repo that'd stop you trusting it on a prod box?

---

## Post 3 — r/SideProject

**Title:** I used an AI agent to build and deploy an API on a $0 infrastructure budget

**Body:**

Over the last week I used an AI agent to help build, test, document, and deploy a small API. I set the constraints and approved account-level actions; the agent handled much of the implementation and verification.

**The product:** MD2HTML — Markdown-to-HTML plus developer utility endpoints. POST data, get a deterministic JSON response. It is intentionally small and uses Python's standard library.

**What is verified:**
- Python stdlib server with 26 advertised endpoints
- Unit tests, OpenAPI coverage checks, and live health checks
- Reverse proxy deployment on an existing Oracle free-tier VPS
- 10 free billable calls, then a published LTC payment address
- Source, docs, SDKs, and distribution drafts

**Current scoreboard:**
- ✅ API live: http://147.15.103.217/md2html/
- ✅ Source public: https://github.com/danielbenevides-ops/md2html-api
- ✅ Payment watcher tested against a zero-balance address
- ❌ Confirmed paying customers: 0
- ❌ Confirmed revenue: 0 LTC
- Infrastructure spend: $0.00

**Honest part:** shipping was easier than earning trust and finding a real user. This is a feasibility test: an agent can accelerate the build loop, but distribution and conversion still need evidence.

Feedback on the API surface, payment friction, or anything in the repo that would block production use is welcome.
