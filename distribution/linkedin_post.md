# MD2HTML API: Markdown to clean HTML, one API call away

Built a developer tool this week. Problem was simple enough to be annoying: I kept converting Markdown to HTML by hand (or with yet another npm package I didn't want to maintain). So I shipped an API for it.

**MD2HTML API** — send Markdown, get clean HTML back. No bloat, no signup wall, no 47-step onboarding.

What it does:
- REST endpoint for Markdown → HTML conversion
- Runs on a free VPS (yes, really)
- Micro-payment pricing — pay fractions of a cent per call
- Open source: github.com/dcn13l/md2html-api

The indie hacker angle: I wanted to prove you can ship a useful dev tool without $500/mo in infra. Free-tier VPS + lean code + micro-payments = a real product with near-zero fixed cost. Bootstrap-friendly, side-project-friendly, "I have an idea on Sunday night"-friendly.

If you've ever:
- Needed HTML output from Markdown in a pipeline
- Wanted to avoid adding another dependency to your project
- Been curious about micro-payment economics on a real API

…give it a spin: http://147.15.103.217/md2html/

Code, docs, and the "how I kept this at $0/mo" story are on GitHub. Feedback welcome — especially the "this would be more useful if…" kind.

#developer #indiehacker #sideproject #devtools #microservices
