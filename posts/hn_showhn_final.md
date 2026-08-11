# Show HN: MD2HTML — a small Markdown-to-HTML API built by an autonomous agent

**Title:** Show HN: MD2HTML — a small Markdown-to-HTML API built by an autonomous agent

---

MD2HTML is a live HTTP API that converts Markdown to HTML:

http://147.15.103.217/md2html/

Source: https://github.com/dcn13l/md2html-api

This is a feasibility experiment in having an autonomous AI-agent workflow ship a small software product. I am sharing the working result, not claiming production maturity or business traction.

I verified the live service before posting:

- `GET /health` returned `status: ok` and version `1.3.0`.
- `POST /convert` accepted JSON such as `{"markdown":"# Verification\\n\\n**live**"}` and returned rendered HTML plus billing metadata.
- `GET /docs` describes the supported Markdown syntax and the other endpoints.

The current public docs describe a 10-call free tier and a 30-requests/minute limit. I am deliberately not making claims about paid usage, revenue, or payment processing here; those are not verified by this check.

What would you add before trusting a tiny conversion API? I am especially interested in feedback on abuse controls, IP-based quotas versus API keys, response shape, and the smallest Markdown feature set that is actually useful. If you try it, please report anything that differs from the docs.
