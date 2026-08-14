# MD2HTML API — Autonomous Business Experiment

## Overview
MD2HTML API is a Markdown-to-HTML conversion API built entirely by an autonomous AI agent (Hermes by Nous Research) as part of a 30-day $0-budget experiment.

## Live Endpoints
- API: http://147.15.103.217/md2html/
- GitHub: https://github.com/danielbenevides-ops/md2html-api
- Release: https://github.com/danielbenevides-ops/md2html-api/releases/tag/v1.1.0

## Architecture
- Python stdlib only (no external dependencies)
- http.server.ThreadingHTTPServer (DoS resistant)
- systemd service (auto-restart on crash/reboot)
- nginx reverse proxy on Oracle Cloud ARM VPS

## Security
- XSS protection (javascript:/data:/vbscript: schemes blocked)
- Rate limiting: 30 req/min per IP
- Body cap: 1MB
- CORS + security headers
- Global try/except (no stack trace leaks)

## Pricing
- 10 free calls
- 0.001 LTC per 100 calls via Litecoin (no Stripe/KYC/accounts)
- Direct on-chain payments

## Team
Built by 15 AI agents in 5 squads (Produto, Distribuição, Pagamento, Crescimento, Operações).

## Cron Jobs
- Every 3h: 15-agent fan-out to iterate product + distribution
- Every 5min: health monitor (restart if down)
- Daily 20:00: HTML report

