# Why We Built a Free Markdown API with Crypto Micropayments

**Target keywords:** markdown to html api, markdown api free, convert markdown api

Every developer has written this line of code:

```
markdown => html
```

And every developer has then spent the next four hours picking a library, arguing about CommonMark vs GFM, wiring up a sanitizer, patching a CVE, and wondering why converting text is *still* a problem in 2026.

We got tired of it. So we built a free **markdown to html api** and put it on the internet. This is the story of why, and how it works.

---

## The problem we kept hitting

Markdown is the lingua franca of the web. Readmes, docs, chat, tickets, LLM output — it's all Markdown. But every project we touched solved the same problem a different way:

- **Team A** used `marked.js` on the client and got an XSS bug from an unfiltered link.
- **Team B** used Python's `markdown` library on the server and spent a weekend debugging a plugin incompatibility.
- **Team C** used a static site generator and couldn't accept user-submitted Markdown at all.
- **Team D** paid for a SaaS-renderer that went down during a launch.

Same problem. Four different disasters. The common thread: **converting Markdown to HTML should not be a project.** It should be a function call — and that function call should work the same way everywhere, with sanitization handled for you.

That's the whole pitch. We built an API that does that, and we made it free.

---

## What we built

A dead-simple **markdown to html api**:

- **Endpoint:** `POST http://147.15.103.217/md2html/`
- **Input:** JSON with a `markdown` field
- **Output:** JSON with an `html` field — sanitized, ready to render
- **No API key** for light use
- **Open source:** [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api)

### cURL

```bash
curl -X POST http://147.15.103.217/md2html/ \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold**."}'
```

### Python

```python
import requests
r = requests.post(
    "http://147.15.103.217/md2html/",
    json={"markdown": "# Hello\n\nThis is **bold**."}
)
print(r.json()["html"])
```

### JavaScript

```javascript
const res = await fetch('http://147.15.103.217/md2html/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ markdown: '# Hello\n\nThis is **bold**.' })
});
const { html } = await res.json();
```

Sanitization runs server-side. Output is clean. Your frontend stays dumb and safe.

---

## Why free, though?

Because charging for a Markdown parser in 2026 is like charging for a calculator. The value isn't in the conversion — it's in:

1. **Not maintaining it.** Patching libraries is expensive. We patch once; everyone benefits.
2. **Consistency.** Same HTML on web, iOS, Android, edge, server.
3. **Trust.** Open source + a live public endpoint means you can verify the behavior yourself.

We treat it like infrastructure. TLS, HTTP/2, DNS — nobody bills you per request for those. Markdown conversion is in the same category now.

---

## So where do crypto micropayments come in?

Free has a cost. Servers, bandwidth, and the time to patch the parser when a new edge case ships. Most "free" APIs handle this two ways:

- **Ads.** Gross. We won't put ads in your HTML.
- **Vendors lock-in.** The first 1,000 calls are free, then $49/mo, then a sales call. We hate that.

We wanted a third option: **pay-per-request, at true cost, with no middleman.** That's crypto micropayments.

### How it works

- **Light use:** Free, no signup. If you're converting a few dozen Markdown documents a day, just call the API.
- **Heavy use:** Pay per request with a crypto wallet. We're talking fractions of a cent per call — true cost of the compute, no subscription, no markup. No payment processor skimming 2.9% + $0.30, because at $0.001/request the processor fee would cost more than the request itself. Only pure crypto settlement keeps micropayments *micro*.

The endpoint is the same. The pricing is honest. You scale from "free hobby project" to "production at volume" without rewriting a single line of code or talking to a sales rep.

---

## What's actually in the request

```bash
# Basic conversion — free tier
curl -X POST http://147.15.103.217/md2html/ \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Title\n\n- item one\n- item two\n\n```code block```"}'
```

```bash
# Same call, with a crypto payment header for high-volume access
curl -X POST http://147.15.103.217/md2html/ \
  -H "Content-Type: application/json" \
  -H "X-Micro-Payment: <signed-payment-token>" \
  -d '{"markdown": "# Title\n\n- item one\n- item two"}'
```

Same output. Same endpoint. The only difference is whether you're in the free tier or paying per request.

---

## What we learned shipping it

1. **Most people need way less than they think.** 90% of Markdown-to-HTML use cases are: headers, bold, italic, lists, code blocks, links. A robust **markdown to html api** that handles those well beats an over-engineered parser that does everything poorly.
2. **Sanitization is the real product.** Nobody asks for it until they get an XSS bug. Then it's the only thing they care about.
3. **Crypto lets you be honest about cost.** When a request costs $0.0003 in compute, charging $0.001 is fair. A credit-card processor won't even let you *sell* something for $0.001. Crypto does. That's why micropayments work for us and subscriptions don't.
4. **Open source is a feature, not a concession.** People trust the API because they can read the code. [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api). Fork it, audit it, self-host it. We'd rather have honest users than trapped ones.

---

## Try it

Free tier, no signup. One cURL command:

```bash
curl -X POST http://147.15.103.217/md2html/ \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\n\n**This works.**"}'
```

If you build something with it, tell us. If you find a bug, open an issue. If you want to self-host, the code is right there.

**Links**
- API: `http://147.15.103.217/md2html/`
- Source: [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api)

Stop maintaining a Markdown parser. Start shipping features.
