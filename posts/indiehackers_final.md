---
title: "My First Goal Isn't $10K MRR — It's $1 in Revenue"
platform: indiehackers
status: not_posted_no_auth
word_count: 231
---

# My First Goal Isn't $10K MRR — It's $1 in Revenue

I just launched [MD2HTML API](https://147.15.103.217.sslip.io/md2html/), a small Markdown-to-HTML service. The current public contract is deliberately simple: send a request to `POST /md2html/convert`.

The service is health-checked at version 1.5.0. It includes **10 free calls**. After that, usage is **0.001 LTC per 100 calls, settled in Litecoin (LTC)**, with a limit of **30 requests per minute**. The implementation and API details are linked from the project repository: https://github.com/danielbenevides-ops/md2html-api.

This is an early launch, so I am not claiming users, revenue, or product-market fit. My first measurable milestone is one verified paid call; the next is **$1 in cumulative revenue**. Because this is pay-per-call rather than a subscription, “MRR” is not the right metric for the current offer.

I am sharing the contract openly instead of presenting an unverified technology stack or inflated adoption numbers. If you build tools that need lightweight Markdown conversion, try the free calls and tell me what breaks. Feedback on the endpoint, limits, and Litecoin payment flow is especially useful.

The goal is modest: earn the first dollar honestly, then improve the product based on real usage.

---

*MD2HTML API: https://147.15.103.217.sslip.io/md2html/ — 10 free calls, then 0.001 LTC per 100 calls settled in LTC; 30 requests per minute.*
