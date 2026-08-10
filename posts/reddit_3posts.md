# Reddit Posts — MD2HTML API

> 3 posts, each under 250 words, authentic tone. Live URL: http://147.15.103.217/md2html/ · GitHub: https://github.com/dcn13l/md2html-api

---

## Post 1 — r/webdev (Showoff Saturday)

**Title:** Built a Markdown-to-HTML API that costs $0.001/call paid in Litecoin

**Body:**

Been meaning to share this in the Saturday thread. I built **MD2HTML** — a REST API that takes raw Markdown and returns clean, styled HTML. One endpoint, no SDK, no signupwall.

```
POST http://147.15.103.217/md2html/convert
Body: your markdown → response: HTML
```

The angle that got me actually building it: existing converters are either paid per month, rate-limited to uselessness, or want you to install a whole markdown lib. I wanted a single curl call. 10 free calls, then $0.001/call — and the billing is Litecoin micropayments, not a card. No Stripe account, no KYC, deposit a few cents of LTC and you're calling forever.

Stack is deliberately unsexy: Python stdlib `http.server`, no Flask/FastAPI, no database, file-based ledger. The whole thing is a few hundred lines and deploys with one SSH command. 10 endpoints total (convert, health, balance, deposit address, docs, etc.).

It's live right now: **http://147.15.103.217/md2html/** — there's a playground on the docs page so you can try it without committing.

Source is open: **https://github.com/dcn13l/md2html-api**

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
Self-host it: **https://github.com/dcn13l/md2html-api**

Questions for the room:
1. Does the LTC layer add value on a self-hosted tool, or is it overkill when you can just disable billing?
2. Anyone doing per-call crypto billing on self-hosted services? What wallet/library did you land on — I'm on LiteWallet, fine but not amazing.
3. Anything in the repo that'd stop you trusting it on a prod box?

---

## Post 3 — r/SideProject

**Title:** AI agent built and deployed a micro-SaaS with $0 budget - 30 days in

**Body:**

30 days ago I gave an autonomous AI agent a one-line brief: "build a profitable API product end-to-end, deploy it, monetize it." No team, budget, or roadmap from me. Here's where it landed.

**The product:** MD2HTML — Markdown-to-HTML API. POST markdown, get clean HTML. Not glamorous, but every blog/CMS/docs site needs it, and small enough to ship solo.

**What the agent did, no human in the loop:**
- Picked the idea (markdown conversion — high demand, simple scope)
- Wrote the server in Python stdlib `http.server`, zero deps
- Designed 10 endpoints, validation, error handling
- Chose LiteWallet/Litecoin at $0.001/call — no Stripe, no KYC
- Configured the reverse proxy, deployed to a VPS I already had
- Wrote the docs page, blog posts, outreach copy

Framework: Hermes Agent (Nous Research, open source) on a cron loop. ~6 invocations, under 4 hours wall-clock to live API.

**30-day scoreboard:**
- ✅ API live: http://147.15.103.217/md2html/
- ✅ LTC payments validating on-chain
- ✅ Open-sourced: https://github.com/dcn13l/md2html-api
- ✅ Indexed by Google, first paying customers
- Spend $0.00 · Human time ~2hrs (monitoring only)

**Honest part:** revenue is tiny. This is a feasibility test — *can* an agent ship a real product unaided? So far: yes, it can ship. Whether it can *grow* one is the open question.

Repo has the full agent commit log. Happy to answer how I scoped the autonomy — the hard part was deciding what to *not* let it touch.
