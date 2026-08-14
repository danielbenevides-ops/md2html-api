# Self-Hosted API Services: A Developer's Guide to MD2HTML

*Targeting the keyword: **convert markdown to html programmatically***

Most Markdown rendering happens inside a build step — Jekyll, Hugo, VitePress, Astro. That works until you need to **convert markdown to html programmatically** from a service that isn't a static-site generator: an API backend that accepts rich-text submissions, a Slack or Discord bot that pretty-prints documentation, a documentation portal that renders README files on the fly, or an editor that needs a live preview served from the same backend that does the final render.

When you reach that point, you have two real options:

1. Bundle a Markdown parser into every service that needs one, in whatever language each service is written in, and accept the configuration drift.
2. Stand up one HTTP service that does the conversion and call it from everywhere.

Option 2 is what [MD2HTML](https://147.15.103.217.sslip.io/md2html) is. This guide shows how to use it, how to self-host it, and where it fits.

## What the API does

One endpoint: `POST /convert`. You send a JSON body containing Markdown, you get back a JSON body containing HTML. No auth on the free tier (10 calls), then pay-per-call in Litecoin. The source is open at [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api), so you can run the same thing on your own infrastructure.

### Quick example

```bash
curl -X POST https://147.15.103.217.sslip.io/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Quick start\n\n- item one\n- item two\n\n```js\nconst x = 1;\n```"}'
```

```json
{
  "html": "<h1>Quick start</h1>\n<ul>\n<li>item one</li>\n<li>item two</li>\n</ul>\n<pre><code class=\"language-js\">const x = 1;</code></pre>"
}
```

## Calling it from your stack

**Python** (backend handler, lint step, CI script):

```python
import requests

def md_to_html(markdown_text: str) -> str:
    r = requests.post(
        "https://147.15.103.217.sslip.io/md2html/convert",
        json={"markdown": markdown_text},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["html"]

print(md_to_html("# Hello\n\nA **paragraph**."))
```

**Node.js / TypeScript** (serverless function, editor preview backend):

```typescript
async function mdToHtml(markdown: string): Promise<string> {
  const res = await fetch("https://147.15.103.217.sslip.io/md2html/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });
  if (!res.ok) throw new Error(`convert failed: ${res.status}`);
  const { html } = await res.json() as { html: string };
  return html;
}
```

**Go** (CLI tool, microservice):

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func mdToHTML(md string) (string, error) {
    body, _ := json.Marshal(map[string]string{"markdown": md})
    resp, err := http.Post("https://147.15.103.217.sslip.io/md2html/convert",
        "application/json", bytes.NewReader(body))
    if err != nil { return "", err }
    defer resp.Body.Close()
    var out struct{ HTML string `json:"html"` }
    json.NewDecoder(resp.Body).Decode(&out)
    return out.HTML, nil
}

func main() {
    h, _ := mdToHTML("# From Go\n\nA list:\n\n- a\n- b\n")
    fmt.Println(h)
}
```

The point: every runtime that can POST JSON gets the same HTML. No per-language parser config, no per-language extension list.

## Self-hosting

The hosted endpoint is convenient for kicking the tires (the 10 free calls are enough to wire up a pipeline and see if the output matches what you want). For production you'll usually want your own instance — full control, no per-call cost, no network round-trip to a third party.

```bash
git clone https://github.com/danielbenevides-ops/md2html-api.git
cd md2html-api
# follow the README — typically: install deps, set PORT, run
```

Run it behind nginx or Caddy with TLS, put it on an internal address, and point your services at `http://md2html.internal:8777/convert`. Because the contract is just "POST Markdown, get HTML," swapping the hosted API for your own instance is a one-line base-URL change in each client.

## When this beats a bundled parser

- **Multiple runtimes need the same output.** One parser, one set of rules, one upgrade.
- **Untrusted input.** Centralize the sanitization — strip raw HTML, enforce `safe` mode, allowlist tags — in one place instead of in every consumer.
- **Serverless / edge cold starts.** A bundled CommonMark + GFM parser inflates the function image; a network call to an internal service is cheap and warm.
- **Editor previews.** The preview your authors see during editing is produced by the same service that produces the final published HTML, so what they see is what ships.

If you only ever render Markdown inside one SSG build, keep the bundled parser. The moment rendering spreads out, a single conversion service is the simpler design — and MD2HTML is a small, open, self-hostable way to get one running.

## Links

- API: <https://147.15.103.217.sslip.io/md2html>
- Source: <https://github.com/danielbenevides-ops/md2html-api>
