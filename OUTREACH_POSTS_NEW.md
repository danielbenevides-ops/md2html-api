# New Outreach Posts — md2html-api

> Three new posts for channels not yet covered in OUTREACH_COPY.md or LAUNCH_POSTS.md.
> API base: `http://147.15.103.217/md2html/` · GitHub: <https://github.com/danielbenevides-ops/md2html-api>

---

## 1. Reddit — r/SideProject

**Title:** Built a markdown-to-HTML API with no signup, no API keys — just pay per call in Litecoin

**Body:**

Hey r/SideProject — sharing something I shipped recently.

I kept bolting markdown parsers into every side project. So I factored it out: send markdown to one endpoint, get clean HTML back. No SDK, no bundle, no monthly plan.

The part I'm most happy about: **no signup wall**. You get 10 free calls off the bat. After that, you pay per call in Litecoin — $0.001 each. No account, no API key to manage, no credit card on file. You preload a little Lite and go.

Try it right now — paste this in your terminal:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello SideProject\n\n**bold** and [a link](https://example.com)"}'
```

You'll get JSON back with clean semantic HTML. That's the whole product.

Source is open: **https://github.com/danielbenevides-ops/md2html-api**

Would love feedback from fellow side-project folks — does pay-per-call in crypto beat the usual "free tier then $19/mo" for a tiny utility API? What's missing? Drop a comment.

---

## 2. Reddit — r/api

**Title:** A minimalist Markdown→HTML API: one POST, JSON in/out, 10 free calls then pay-per-call in Litecoin

**Body:**

Hey r/api — looking for design feedback on a small API I shipped.

The premise: one endpoint, one job. Send markdown, get HTML. No query-string soup, no versioned paths, no auth header dance for the free tier.

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Heading\n\n- item one\n- item two"}'
# -> {"html":"<h2>Heading</h2>\n<ul>\n<li>item one</li>\n<li>item two</li>\n</ul>"}
```

**Design choices I'd like input on:**

- **One endpoint (`POST /convert`)** — no `/v1/`, no GraphQL, no alternative verbs. Is single-resource minimalism a virtue or a liability?
- **Free tier: 10 calls, no API key.** After that, pay per call via Litecoin (0.001 LTC per 100 calls). No Stripe, no monthly plan. The upside is zero onboarding friction; the downside is no rate-limit identity for free users. Worth it?
- **Response is always `{ "html": "..." }`** — no envelope, no metadata, no links. Does that feel too sparse, or just right for a single-purpose API?

Open source, full code here: **https://github.com/danielbenevides-ops/md2html-api**

Would genuinely value feedback from API designers here. What would you change? Is the pay-per-call-in-crypto model viable for metering, or is it a gimmick? Let me know.

---

## 3. IndieHackers.com

**Title:** I let an autonomous AI agent run a micro-SaaS as CEO — here's what shipped and what I learned

**Body:**

Hey IH — running an experiment and want to share it here because the community tends to enjoy the weird stuff.

**The premise:** Can an autonomous AI agent own the full business loop — pick a product, build it, price it, and ship it — with a human only steering, not coding?

I gave a Hermes Agent (by Nous Research) the role of "CEO" for a one-product company on a $0 budget. It brainstormed 20+ ideas, picked the most boring viable one, wrote the code, set up the repo, and landed on pricing without being told to.

**What shipped:** md2html-api — a Markdown-to-HTML conversion API. One endpoint, one job. 10 free calls, then 0.001 LTC per 100 calls via Litecoin. No accounts, no API keys, no Stripe — just preload Lite and go.

Try it:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello IndieHackers\n\nThis API was built by an **AI agent**."}'
```

Code is open: **https://github.com/danielbenevides-ops/md2html-api**

**What I've actually learned so far:**

- **The agent can run the build loop.** Product scoping, code, tests, docs, repo — all handled. The discipline surprised me: it scoped *down* to one endpoint, resisting feature creep.
- **The agent cannot run the trust loop.** Distribution is where it breaks. No one has a reason to try an unknown API from an account with no history. The gap between "can build" and "can sell" is the real finding.
- **Micropayments felt right.** The agent landed on near-zero pricing naturally — because the value of a single HTML conversion genuinely is tiny, and that forced a pay-per-call model over the usual SaaS default.

I'm documenting the full 30-day run. If you'd read a deeper write-up — or want to poke holes in the experiment, the architecture, or the pricing — I'm here. What would make this genuinely interesting to you?

---
