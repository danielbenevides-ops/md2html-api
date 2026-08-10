# I built a Markdown-to-HTML API on a free Oracle VPS — here's the story

Hey r/SideProject,

Solo dev here. Wanted to share something I built and actually shipped.

## The problem

I kept needing to convert Markdown to HTML from different apps and scripts. Every time, I either pulled in a heavy library or got inconsistent output. I just wanted a dead-simple endpoint: send Markdown, get clean HTML back. Nothing fancy.

## What I built

**MD2HTML API** — a lightweight HTTP API that takes Markdown in and returns HTML. No auth, no rate limits (yet), no signup. Just hit the endpoint and go.

- API URL: http://147.15.103.217/md2html/
- GitHub: https://github.com/dcn13l/md2html-api

## The build

I'm solo — no team, no budget, no investors. I ran the whole thing on an **Oracle Cloud free-tier VPS** (the Always Free ARM instance with decent specs for $0/month). Honestly, that free box is the only reason this exists. I couldn't justify paying for hosting on a side project with zero users.

Stack is nothing exotic: a small server, a Markdown parser, and a route that glues them together. Part of the project is auto-orchestrated (I used Hermes Agent to scaffold and test parts of the workflow), but all the design decisions, deployment, and debugging were mine.

## What I learned

- Oracle's free tier is genuinely good for solo devs. The ARM instance has real resources. Setup was the hardest part — their networking docs are a maze.
- "Ship ugly, iterate" is real. I spent way too long polishing before launch. Could've shipped two weeks earlier.
- Solo + free tier means you own every layer: code, deploy, DNS, firewall, monitoring. Slow but you learn a ton.
- Automating the boring parts (scaffolding, test generation) with an agent saved real time. It didn't write the core logic — I did — but it handled enough boilerplate that I stayed in the zone.

## What's next

- Auth and API keys (optional, for heavier users)
- Rate limiting
- More Markdown flavor support
- Maybe a tiny dashboard for usage stats

## Try it

Just hit the API with Markdown and get HTML back:

```
GET http://147.15.103.217/md2html/?md=**hello%20world**
```

Repo, issues, and suggestions welcome: https://github.com/dcn13l/md2html-api

If you've built something on Oracle's free tier, I'd love to hear how it's holding up. And if you've got feedback on the API or want a feature, drop it here or open an issue.

Thanks for reading.
