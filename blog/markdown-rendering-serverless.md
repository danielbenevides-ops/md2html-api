# Markdown Rendering Serverless: A Practical Pattern for Jamstack and Beyond

Serverless functions and static site generators were made for each other — until you need to render Markdown authored by users at runtime. Bundling a parser into every Lambda cold start bloats your deployment artifact and slows invocation times. Keeping markdown rendering serverless with a dedicated HTTP API solves both problems cleanly.

## The Problem with Bundled Renderers

Serverless functions have tight limits. AWS Lambda caps deployment packages at 50 MB zipped; Cloudflare Workers runs in a V8 isolate with strict memory ceilings. Drop a full Markdown library — plus its syntax-highlight plugin, its footnote extension, its table parser — and you're spending a third of that budget on a renderer you only call occasionally. Cold starts suffer. Iteration slows. For what?

## A Leaner Pattern

Call the rendering out to a markdown to html api instead. Your function stays tiny, your dependency list stays empty, and the actual compute happens somewhere designed for it:

```javascript
export async function handler(request) {
  const body = await request.json();
  const res = await fetch("https://147.15.103.217.sslip.io/md2html/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown: body.markdown })
  });
  const { html } = await res.json();
  return new Response(html, {
    headers: { "Content-Type": "text/html" }
  });
}
```

That's the whole function. No imports beyond the platform's native `fetch`. Markdown goes in, HTML comes out, and your serverless runtime stays under a kilobyte of application code.

## Why This Beats Self-Bundling

Keeping markdown rendering serverless means you never ship parser internals to your edge. Three concrete wins:

- **Smaller artifacts.** No parser, no AST, no syntax-highlight grammar files. Your deploy is lean and your cold starts are fast.
- **Consistent output.** The same canonical renderer answers every invocation. Preview, production, and local dev all produce identical HTML.
- **Decoupled upgrades.** When a new Markdown spec drops, the API updates once. You touch nothing.

## Python on AWS Lambda

The same pattern works server-side. Lambda exposes the same `POST` to the endpoint and returns the rendered HTML, with no parser bundled in your zip:

```python
import json
import urllib.request

def lambda_handler(event, context):
    body = json.loads(event["body"])
    req = urllib.request.Request(
        "https://147.15.103.217.sslip.io/md2html/convert",
        data=json.dumps({"markdown": body["markdown"]}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        html = json.loads(resp.read())["html"]
    return {"statusCode": 200, "body": html,
            "headers": {"Content-Type": "text/html"}}
```

## Cost and Trust

The MD2HTML API gives you 10 free calls to prototype against. Beyond that, LTC micropayments unlock additional requests — ideal for a serverless workload where you pay per invocation anyway. No fixed monthly fee means zero spend when traffic is idle, which is exactly how serverless billing is supposed to feel. The renderer's source is open at [github.com/danielbenevides-ops/md2html-api](https://github.com/danielbenevides-ops/md2html-api), so you can audit the conversion logic or self-host if you ever need to pull it back on-platform.

## The Takeaway

Serverless rewards small, focused functions. By pushing Markdown rendering to a dedicated API, you keep your functions lightweight, your cold starts fast, and your dependency surface minimal — while inheriting a renderer that stays current without you touching it. That's markdown rendering serverless done right.
