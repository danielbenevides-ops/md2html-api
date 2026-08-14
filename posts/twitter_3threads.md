# Twitter/X Threads — MD2HTML API (sanitized)

> Three threads for official X posting. Each tweet is under 280 characters. Copy is limited to verified service facts.

---

## Thread 1 — "A small Markdown-to-HTML API" (7 tweets)

**1/7**
MD2HTML API: a small HTTP service that converts Markdown to HTML. 📄➡️🌐

Try the live service:
https://147.15.103.217.sslip.io/md2html/

Here are the verified API details 👇🧵

**2/7**
The conversion route is:

POST https://147.15.103.217.sslip.io/md2html/convert

Send Markdown as JSON, for example `{"markdown":"# Hello **world**"}`, and the service returns HTML in JSON.

**3/7**
The live health endpoint reports version `v1.5.0`:

https://147.15.103.217.sslip.io/md2html/health

Source code and project documentation:
https://github.com/danielbenevides-ops/md2html-api

**4/7**
The pricing model is pay-per-call:

• 10 free calls
• Then 0.001 LTC per 100 calls
• Payment currency: LTC

Current pricing details:
https://147.15.103.217.sslip.io/md2html/pricing

**5/7**
The documented request limit is 30 requests per minute.

Read the live usage guide before integrating:
https://147.15.103.217.sslip.io/md2html/docs

**6/7**
Quick test with curl:

`curl -X POST https://147.15.103.217.sslip.io/md2html/convert -H 'Content-Type: application/json' -d '{"markdown":"# Hello"}'`

Use the docs to confirm the response shape.

**7/7**
MD2HTML is an option for developers looking for a focused Markdown-to-HTML HTTP endpoint with a free allowance and pay-per-call LTC pricing.

Evaluate it here:
https://147.15.103.217.sslip.io/md2html/

---

## Thread 2 — "Trying the API with a minimal HTTP client" (5 tweets, technical)

**1/5**
You can try MD2HTML with a plain HTTP request:

1. POST Markdown to `/md2html/convert`
2. Send JSON with a `markdown` field
3. Read the returned HTML JSON

Live base URL:
https://147.15.103.217.sslip.io/md2html/

**2/5**
A documented request looks like this:

`curl -X POST https://147.15.103.217.sslip.io/md2html/convert -H 'Content-Type: application/json' -d '{"markdown":"# Hello **world**"}'`

The service also documents raw `text/plain` Markdown input.

**3/5**
The conversion docs cover common Markdown such as:

• Headings
• Bold and italic text
• Links
• Inline and fenced code
• Unordered lists

Full reference:
https://147.15.103.217.sslip.io/md2html/docs

**4/5**
Integration details to account for:

• 10 free calls
• 0.001 LTC per 100 calls afterward, in LTC
• 30 requests per minute
• `402` after the free allowance is exhausted

Check the live contract before shipping.

**5/5**
The implementation and documentation are available here:
https://github.com/danielbenevides-ops/md2html-api

Test the live endpoint, inspect the returned HTML, and verify limits and billing behavior for your own use case.

---

## Thread 3 — "Pay-per-call pricing for an API" (5 tweets, technical)

**1/5**
MD2HTML uses a simple published allowance:

• 10 free calls
• Then 0.001 LTC per 100 calls
• LTC is the payment currency

Pricing endpoint:
https://147.15.103.217.sslip.io/md2html/pricing

**2/5**
The live service documents a limit of 30 requests per minute.

That matters when adding a client: keep requests within the published window and handle rate-limit responses explicitly.

Usage guide:
https://147.15.103.217.sslip.io/md2html/docs

**3/5**
For conversion, send a POST request to:

https://147.15.103.217.sslip.io/md2html/convert

The first 10 billable calls are free. After that allowance is exhausted, billed POST requests return payment-required information.

**4/5**
For current service and billing details, use the public endpoints directly:

Health: https://147.15.103.217.sslip.io/md2html/health
Pricing: https://147.15.103.217.sslip.io/md2html/pricing
Payment: https://147.15.103.217.sslip.io/md2html/payment

**5/5**
Project source:
https://github.com/danielbenevides-ops/md2html-api

If the model fits your workload, start by testing Markdown conversion, then review the documented response, free allowance, price, and rate limit before production use.

---

*Sanitized for official X posting; no post was made by this file update.*
