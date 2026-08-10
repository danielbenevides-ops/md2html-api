# Show HN: AI Agent built a micro-SaaS API with $0 budget

**Title:** Show HN: AI Agent built a micro-SaaS API with $0 budget

---

We built MD2HTML — a live API at http://147.15.103.217/md2html/ that converts Markdown to clean, styled HTML. The product scope was entirely defined and executed by an autonomous AI agent, including the API specification, input validation, error handling, and health endpoint. This is a feasibility experiment: can a non-human agent ship a usable software product end-to-end with literally zero budget allocated for development.

The agent runs on an open-source framework (Hermes Agent by Nous Research) and operates autonomously via a cron-scheduled loop — no human in the loop between planning and deployment. It selected the product idea, wrote the server code in Python, configured the reverse proxy, and deployed to a VPS we already owned (so $0 marginal infrastructure cost). The agent's reasoning, tool calls, and git commits are logged for full transparency. Total time from concept to live API: under 4 hours wall-clock, spanning ~6 agent invocations triggered by cron at 15-minute intervals.

Monetization is a crypto micropayment model using the Lightning Network / USDC on base. API calls are authenticated by a Bearer token tied to a pre-paid balance — users top up via a deposit address, and each request deducts a sub-cent fee (currently $0.0001/KB of output HTML). No Stripe, no KYC, no minimum charge. The balance accounting is a simple SQLite ledger the agent wrote. The goal is to test whether crypto-native micropayments can sustain a product with too small a price-per-call to clear traditional payment-processor minimums.

Feedback we're looking for: (1) Is the crypto micropayment UX acceptable, or is the deposit-then-call flow too much friction for sub-cent transactions? (2) For anyone who deploys autonomous agents — what's your threshold for letting an agent own production deploy access? (3) Any obvious gaps in the API design (rate limiting, idempotency, response caching)? Happy to share the agent's system prompt, commit log, and deployment scripts if there's interest.
