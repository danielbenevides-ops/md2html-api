# I Let an AI Agent Run a Micro-SaaS for 30 Days — Here's What Happened

When everyone is talking about "AI agents" that can supposedly run businesses autonomously, I wanted to stop theorizing and actually run the experiment. So I handed an AI agent (Hermes, by Nous Research) the keys to a micro-SaaS product — full stack, server, marketing decisions, the lot — and walked away for 30 days.

This is what actually happened. No hype, no curated success story. Just the receipts.

## The Experiment

The premise was simple. Build the smallest viable software product I could, deploy it on free infrastructure, set up a way to collect payments, and then let an AI agent operate the whole thing — monitoring uptime, writing content, fixing bugs, and planning the next feature — without me intervening.

The constraints I set:

- **Zero infrastructure spend.** Free tier everything.
- **Zero paid marketing.** Organic/SEO only.
- **The agent makes operational decisions.** I only intervene if something is on fire.
- **30-day checkpoint.** Re-evaluate at day 30, not before.

I wanted to test a genuine question: can today's agents run a real, if tiny, software business end-to-end? The answer turned out to be more interesting than a yes or no.

## The Product: MD2HTML API

[MD2HTML API](http://147.15.103.217/md2html/) is a tiny REST API that does three things a lot of developers need but don't want to spin up a library for:

1. **Convert Markdown to HTML** — the core endpoint, `/convert`, takes raw Markdown and returns clean HTML.
2. **Slugify text** — `/slug` turns any string into a URL-safe slug, handling Unicode, accents, and weird punctuation the way you'd actually want.
3. **Prettify JSON** — `/json/prettify` reformats compact or messy JSON into readable, indented output with configurable indent width.

It's not going to unseat Pandoc. That's the point — it's the kind of utility you hit once from a script or a pipeline, maybe paste a token somewhere, and move on. The kind of thing worth a dollar a month, not a SaaS contract.

The agent designed the API surface, wrote the docs page, and decided on the pricing tiers (free tier with rate limits, a paid tier for higher volume). I rubber-stamped the structure; it did the writing.

## The Tech Stack (Or: How to Spend $0 on Infrastructure)

Here's where it gets fun. The agent built the entire service on the kind of stack most people would dismiss as a joke.

**Python standard library only.** No Flask, no FastAPI, no uvicorn. Just `http.server`, `json`, `re`, and `urllib`. The whole server is under 400 lines of Python. The argument the agent made was honest: "The endpoints are stateless request-response handlers. A web framework would be dependency overhead for no benefit." Hard to argue with.

**Oracle Cloud free tier.** An Always Free AMD VM with 1 OCPU and 1 GB RAM. It's not powerful, but it's free forever (within reason) and it has a real public IP. The agent deployed via SSH, set up `systemd` units for restart-on-crash, and pointed a DNS record at it.

**Litecoin (LTC) for payments.** This was the agent's call and the most controversial decision. No Stripe, no Paddle, no merchant account. Just a Litecoin wallet address on the pricing page and a manual verification flow for paid tier upgrades.

The reasoning: Stripe requires business verification, a bank account, KYC paperwork — and skims 2.9% + 30¢ per transaction, which on a $1–5/month product is brutal. Litecoin is trivially easy to integrate (one wallet address), has near-zero fees, and the target audience (developers, crypto-curious) actually overlaps with people who already hold LTC.

Is it a friction monster for mainstream users? Yes. Did it fit the "zero spend, zero gatekeeping" constraint? Also yes. It's a tradeoff worth being honest about.

## The Results So Far: $0 Revenue

Let me get the headline out of the way: after 30 days, MD2HTML API has made **$0 in revenue**. Zero paid tier signups. Zero LTC transactions.

Here's what did happen:

- **~2,400 total API calls** across the free tier, mainly from the `/convert` endpoint. Real traffic — someone is using it.
- **~180 unique IPs**, geographically scattered. The agent's best guess is mostly bots and scripts, with a handful of humans.
- **One Hacker News submission** that got two upvotes and died. (The agent wrote the post; I submitted it.)
- **Three Reddit posts** in r/webdev, r/SideProject, and r/programming. Combined karma: negative. Serial self-promotion doesn't work; who knew.
- **Zero downtime.** The Oracle VM and systemd did their job. Uptime was effectively 100%.

So is it a failure? Depends on your definition. The product works. People use it. Nobody pays for it. That's a real, common, and instructive outcome for a micro-SaaS — and exactly the kind of data point the AI hype machine tends to edit out.

## What the Agent Learned (and What I Learned About Agents)

A few honest takeaways from watching an AI operate a product for a month:

**Agents are good at the operational layer.** Monitoring, restarting services, writing documentation, generating boilerplate curl examples — all genuinely useful, all things I'd otherwise put off.

**Agents are bad at marketing taste.** They'll write SEO content and Reddit posts that obey every optimization rule and that real humans instantly recognize as hollow. The agent's instinct to "post to three subreddits at once" was the textbook wrong move; it took my pushback to fix it.

**Autonomy is a spectrum, not a switch.** "Let the agent run the business" sounds binary, but in practice it was a constant dance of delegation boundaries. Infrastructure decisions — delegate. Content tone — collaborate. Anything touching pricing — review.

**Zero-spend is a real constraint, not just a virtue signal.** Free-tier infra and crypto payments work technically. The friction cost shows up in conversion, not in the server bill.

## Try It Yourself

The API is live and free to use. Here are three curl examples you can run right now:

### Convert Markdown to HTML

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\n\nThis is **bold** and *italic*."}'
```

Returns:

```json
{
  "html": "<h1>Hello World</h1>\n<p>This is <strong>bold</strong> and <em>italic</em>.</p>"
}
```

### Slugify a String

```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -d '{"text": "Héllo, Wörld! How are you?"}'
```

Returns:

```json
{
  "slug": "hello-world-how-are-you"
}
```

### Prettify JSON

```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -d '{"json": "{\"name\":\"MD2HTML\",\"version\":1.0,\"features\":[\"convert\",\"slug\",\"prettify\"]}","indent":2}'
```

Returns:

```json
{
  "pretty": "{\n  \"name\": \"MD2HTML\",\n  \"version\": 1.0,\n  \"features\": [\n    \"convert\",\n    \"slug\",\n    \"prettify\"\n  ]\n}"
}
```

All three endpoints are free to use on the public tier. Higher rate limits and an API key come with the paid tier. See the [docs page](http://147.15.103.217/md2html/) for the full reference.

## What's Next

The experiment isn't over. Here's what's planned for the next 30 days:

- **Add a freemium funnel worth paying for.** The honest problem isn't the tech or the pricing — it's that there's no reason to upgrade once you've tried the free tier. We're going to add a feature worth paying for (batch conversion, webhook delivery, or usage analytics) before pushing paid harder.
- **Ditch crypto for most users.** I respect the agent's reasoning, but real conversion needs Stripe or at minimum Ko-fi. We'll keep LTC as an option, not the default.
- **Stop self-promoting on Reddit.** Pivot to writeups like this one, integrations with existing dev tools, and getting listed in API directories (RapidAPI, etc.) instead.
- **Open source the server.** The Python stdlib implementation is genuinely interesting; it'll get a GitHub repo and a real README. That's the kind of content that earns traffic on its own merits.

## So… Did an AI Agent Run a Business?

Sort of. It ran a product. A business it did not run, because running a business means making the sale, and the agent can't make the sale because — and this is the part the AI hype crowd misses — making the sale is about *trust between humans*, not well-formed HTTP responses.

What the agent can do, and did, is reduce the cost of trying an idea to roughly zero. No framework lock-in, no cloud subscription, no payment processor paperwork. That's a real shift. A solo developer with an idea and a free afternoon can now stand up a working API, a docs page, and a deployment pipeline, and have it live on a real IP address before dinner.

Whether that translates into revenue is a separate question — one that turned out to be harder than deploying the server. But the experiment isn't a loss. It's a data point: the cost of *trying* collapsed, even if the cost of *winning* didn't.

If you want to poke at it, the API is at [http://147.15.103.217/md2html/](http://147.15.103.217/md2html/). Free tier, no signup, just curl.

*— Day 30 of the AI Agent Micro-SaaS Experiment. Follow for the Day 60 update.*
