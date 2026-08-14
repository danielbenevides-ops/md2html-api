# Embed a Markdown Renderer With No Dependencies (Python, JavaScript, curl)

**Target keyword:** convert markdown without dependencies

Adding Markdown rendering to a project usually means picking a library, pinning a version, and maintaining it across every runtime that needs to render. That's a lot of overhead for what is, at heart, a text-to-HTML step. This tutorial shows how to **convert markdown without dependencies** by calling the free MD2HTML API over plain HTTP — from `curl`, Python, and JavaScript — with no SDK, no `package.json` entry, and no pip install.

The API is live at `http://147.15.103.217/md2html/`. The conversion endpoint is `POST /convert`, the body is JSON containing your Markdown, and the response is JSON containing the rendered HTML. The first 10 calls per client are free.

## The contract (one endpoint)

```
POST http://147.15.103.217/md2html/convert
Content-Type: application/json
X-API-Key: mk_...   (optional — without it, billing falls back to your IP)

{"markdown": "# Hello\n\n**bold** and *italic*."}

-> {"html": "<h1>Hello</h1>\n\n<strong>bold</strong> and <em>italic</em>.",
    "billing": {"status": 200, "calls_made": 1, "remaining": 9, "free_tier_limit": 10}}
```

That's the entire surface. Anything that can POST JSON can render Markdown.

## 1. curl — zero install, zero dependencies

If you have a shell, you have a Markdown renderer. This is the fastest way to **convert markdown without dependencies** in a CI step, a Makefile, or a one-off script:

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello **world**\n\n- one\n- two\n\n[link](https://example.com)"}'
```

Pipe Markdown from a file and save just the HTML field with `jq`:

```bash
curl -s -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d "$(jq -Rs '{markdown: .}' README.md)" | jq -r .html > README.html
```

Here `jq -Rs` slurps the whole file into a JSON string and wraps it as `{"markdown": "..."}`. No parser, no library, no pipeline beyond curl + jq (both pre-installed on most CI runners).

## 2. Python — standard library only

Skip `pip install markdown`. The Python standard library ships everything you need — `urllib.request` for the POST and `json` for the body. This snippet runs on a bare CPython with nothing installed:

```python
import json
import urllib.request

def markdown_to_html(markdown: str) -> str:
    payload = json.dumps({"markdown": markdown}).encode("utf-8")
    req = urllib.request.Request(
        "http://147.15.103.217/md2html/convert",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["html"]

if __name__ == "__main__":
    md = """# Hello world

This is **bold** and *italic*.

- item one
- item two
"""
    print(markdown_to_html(md))
```

Not a single third-party import. Drop this into a serverless function, a build script, or a bot — it will run anywhere Python runs, with no `requirements.txt` entry to pin or patch.

## 3. JavaScript — fetch, no npm package

Browser and Node 18+ both ship a global `fetch`. No `marked`, no `markdown-it`, no bundle step. This works in a `<script>` tag, a Cloudflare Worker, a serverless function, or a Node REPL:

```javascript
async function markdownToHtml(markdown) {
  const res = await fetch("http://147.15.103.217/md2html/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });
  if (!res.ok) throw new Error(`MD2HTML ${res.status}: ${await res.text()}`);
  const { html } = await res.json();
  return html;
}

// Node — top-level await if your runtime supports it
const md = "# Hello **world**\n\n- one\n- two";
console.log(await markdownToHtml(md));
```

For a debounced live preview in the browser, wrap the call in a `setTimeout` and call it on `input` events — the API is CORS-enabled, so a static site can hit it directly with no backend proxy.

## Optional: an API key for usage tracking

Without a key the API bills against your IP address. Register once to get a stable key and a shared free tier you can monitor:

```bash
curl http://147.15.103.217/md2html/register
# {"api_key":"mk_...","wallet_address":"...","free_tier_limit":10,"calls_made":0,"remaining":10}
```

Then pass the key on every call. In Python add it to the headers dict:

```python
headers={"Content-Type": "application/json", "X-API-Key": "mk_YOUR_KEY_HERE"}
```

In JavaScript add it to the `headers` object. The free tier (10 calls per client) and the 30 req/min rate limit apply per IP or per key.

## When to pick this over a library

- **CI / build steps** that need one less dependency to cache and update.
- **Serverless functions** where a 30–60 KB parser library inflates your deployment artifact.
- **Edge runtimes** (Cloudflare Workers, Deno Deploy) with tight bundle and CPU budgets.
- **Multi-language stacks** that want identical HTML from Python, Node, and shell without porting parser config to each.

## What you give up

You trade local parsing for one network round-trip per call (~10–80 ms). For a single-page app rendering keystroke-by-keystroke, a client library is the right shape. For everything else — server runs, build pipelines, preview panes that debounce — the latency is invisible, and you keep your dependency tree empty and your security surface small (no parser CVEs to track, no sanitizer plugin to keep patched).

## Retry and errors

The API returns standard HTTP codes: `200` with `billing.remaining` on success, `402` once the 10 free calls are spent (with a Litecoin wallet address in the body), `429` if you exceed 30 req/min, and `400` on malformed JSON. Wrap your call in a short retry loop with exponential backoff on `429` and surface `402` to the user as a payment step — the rest of the time the endpoint just returns HTML.

## Start now

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Ship HTML, not parser dependencies"}'
```

API docs at <http://147.15.103.217/md2html/docs>. Source and self-host instructions at [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api).
