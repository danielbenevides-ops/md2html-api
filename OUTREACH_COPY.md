# MD2HTML API — Outreach Copy

API base URL: `http://147.15.103.217:8777`
GitHub: <https://github.com/dcn13l/md2html-api>
Pricing: 10 free calls, then pay per call via Litecoin

---

## 1. Reddit — r/webdev (Show-and-Tell)

**Title:** I built a markdown-to-HTML API — here's how it works

**Body:**

Hey r/webdev — sharing a small side project I shipped last week.

I kept bolting markdown parsers into every side project (docs, blogs, CMS input). Different language, different library, same yak-shave every time. So I factored it out into a tiny HTTP service: send markdown, get clean semantic HTML back, one endpoint.

**How it works:**

```bash
curl -X POST http://147.15.103.217:8777/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello\n\nThis is **bold** and this is [a link](https://example.com)."}'
```

Response:

```json
{
  "html": "<h1>Hello</h1>\n<p>This is <strong>bold</strong> and this is <a href=\"https://example.com\">a link</a>.</p>"
}
```

That's the whole thing. One POST to `/convert`, JSON in, JSON out.

**Details:**

- **Endpoint:** `POST http://147.15.103.217:8777/convert`
- **10 free calls** to try it, then pay per call via Litecoin — no signup wall, no monthly plan
- **Use cases:** CMS input sanitization, docs builds, email templates, AI output rendering, anywhere you'd rather not ship a parser dependency
- **Source:** <https://github.com/dcn13l/md2html-api>

Not trying to replace your in-app GFM/CommonMark renderer — if a library works for you, keep it. This is for when you want a clean service boundary (e.g. untrusted user markdown, serverless functions where you don't want a parser bundle, or a docs pipeline where one service owns the render step).

Would love feedback: what output options would make this worth adopting over your current setup — safe mode, custom renderers, syntax-highlight hooks? Drop a comment.

---

## 2. Hacker News — Show HN

**Title:** Show HN: MD2HTML API – markdown-to-HTML in one POST, pay per call in Litecoin

**Body:**

Hey HN — I built a small markdown-to-HTML API after one too many times bolting a parser into a side project. One POST to `/convert`, you get clean semantic HTML back.

**Problem it solves:** every side project that touches markdown ends up pulling in a parser library (and its transitive deps) just to render a snippet. The cost is trivial in isolation, but the surface area adds up: bundle size, CSP, spec-compliance drift, and a parser sitting in the trust boundary when the markdown is untrusted (CMS, user content, AI output). MD2HTML factors that into a single HTTP call.

- **Endpoint:** `POST http://147.15.103.217:8777/convert`
- **Pricing:** 10 free calls, then pay per call via Litecoin — no monthly fee, no card on file
- **Source (open):** <https://github.com/dcn13l/md2html-api>

Example:

```bash
curl -X POST http://147.15.103.217:8777/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "**hi**"}'
# -> {"html":"<p><strong>hi</strong></p>"}
```

Why pay per call for something libraries do free? Convenience and a clean trust boundary. A pipeline that already speaks HTTP gets a render step without a new dependency. The service owns the parser surface; everything downstream consumes HTML. Litecoμ-based metering keeps the billing honest and unbundleable from usage.

Would love feedback — does pay-per-call for a parser sound useful, or is a library always the right answer here? What's missing (safe mode, sanitize options, custom renderers)?

---

## 3. Dev.to — Tutorial-Style Post

**Title:** Convert Markdown to HTML in One HTTP Call — MD2HTML API Walkthrough

**Body:**

I keep ending up in the same spot on side projects: a docs page, a blog, a `textarea` for user content, and I'm reaching for a markdown parser again. Different language, different library, same dependency drag.

So I built **MD2HTML API** — a tiny HTTP service that turns markdown into clean HTML in one `POST`. No SDK, no bundle. This post walks through using it from Node.js.

### What the API does

One endpoint:

```
POST http://147.15.103.217:8777/convert
```

Send JSON with a `markdown` field, get JSON back with an `html` field. That's it.

- 10 free calls to start
- After that, pay per call via Litecoin — no monthly plan, no card on file
- Open source: <https://github.com/dcn13l/md2html-api>

### Quick test

```bash
curl -X POST http://147.15.103.217:8777/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Title\n\n- one\n- two\n- three"}'
```

```json
{
  "html": "<h1>Title</h1>\n<ul>\n<li>one</li>\n<li>two</li>\n<li>three</li>\n</ul>"
}
```

### Using it from Node.js

Here's a real example — converting a markdown blob to HTML before saving to a database. Drop this into any Node project, no extra dependencies beyond what's already in 18+ (global `fetch`):

```js
async function convertMarkdown(markdown) {
  const res = await fetch("http://147.15.103.217:8777/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });

  if (!res.ok) {
    throw new Error(`MD2HTML request failed: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  return data.html;
}

// Example: render a post body before persisting
async function savePost({ title, markdownBody }) {
  const html = await convertMarkdown(markdownBody);
  // ...save { title, html } to your DB or CMS
  console.log(html);
}

await savePost({
  title: "Hello",
  markdownBody: "## Hello world\n\nThis is **bold** and [linked](https://example.com).",
});
```

Output:

```html
<h2>Hello world</h2>
<p>This is <strong>bold</strong> and <a href="https://example.com">linked</a>.</p>
```

### Where this fits

Use MD2HTML when you want render-as-a-service instead of shipping a parser:

- **CMS / user content:** one service owns the parser surface; your app handles HTML.
- **Docs pipelines:** generate HTML server-side without a build step or parser dep in the repo.
- **Serverless functions:** skip bundling a markdown library into every lambda.
- **AI output:** render model-generated markdown before sending downstream.

### Pricing

10 free calls, then pay per call in Litecoin. No monthly fee, no tiered upsell — you only pay for what you call.

### Try it

- API: <http://147.15.103.217:8777>
- Source & docs: <https://github.com/dcn13l/md2html-api>

If you'd want a different option (sanitize-only mode, syntax highlighting hooks, custom renderer config), open an issue on the repo — I'm actively iterating on what the endpoint should expose.

---

## Quick-Reference

| Item | Value |
|---|---|
| API base | `http://147.15.103.217:8777` |
| Endpoint | `POST /convert` |
| Request | `{"markdown": "..."}` |
| Response | `{"html": "..."}` |
| Free tier | 10 calls |
| Paid | per call via Litecoin |
| GitHub | <https://github.com/dcn13l/md2html-api> |
