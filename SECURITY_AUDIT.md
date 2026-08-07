# Security Audit — server.py (Markdown-to-HTML API)

Reviewed: `server.py` (~98 lines, stdlib `http.server`, port 8777). Free-tier, public-internet exposed.

## Findings

### 1. CRITICAL — Stored XSS via unescaped link href
**Description:** Line 41 emits `<a href="\2">` with the raw URL from markdown. No escaping, no scheme allowlist. Input `[x](javascript:alert(document.cookie))` yields `<a href="javascript:alert(document.cookie)">x</a>`. Code blocks (line 46) are also injected unescaped — though line 15 escaped `<>` first, the placeholder-restore re-injects the *raw* captured block (line 11), bypassing the escape. Any HTML payload wrapped in triple-backticks survives.
**Fix:**
```python
# allowlist schemes; reject everything else
URL_RE = re.compile(r'^https?:|^mailto:|^/i')
def safe_href(url):
    u = url.strip()
    return u if URL_RE.match(u) else '#'
# in md_to_html, replace the link sub:
text = re.sub(r"\[(.+?)\]\((.+?)\)", lambda m: f'<a href="{safe_href(m.group(2))}">{m.group(1)}</a>', text)
# escape code block contents before reinsertion:
for i, code in enumerate(blocks):
    code = code.replace("&","&").replace("<","<").replace(">",">")
    text = text.replace(f"\x00CODE{i}\x00", f"<pre><code>{code}</code></pre>")
```

### 2. HIGH — No CORS / no origin restriction
**Description:** Default stdlib server sends no CORS headers, so browsers *should* block cross-origin reads — but there is no `Access-Control-Allow-Origin` either way, and nothing rejects hostile origins server-side. If a CSP-fixed caller is added later, this becomes a CSRF/credential-theft vector. Binding `0.0.0.0` (line 97) exposes to the whole internet unauthenticated.
**Fix:** Explicitly add a restrictive CORS policy and bind loopback in dev / a reverse proxy in prod.
```python
ALLOWED_ORIGIN = "https://your-product.example.com"
def send(self, code, body, ctype="application/json"):
    ...
    self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
    self.send_header("Vary", "Origin")
    self.send_header("X-Content-Type-Options", "nosniff")
# prod: http.server.HTTPServer(("127.0.0.1", PORT), Handler) + nginx in front
```

### 3. HIGH — No rate limiting (DoS)
**Description:** No per-IP limits. A trivial loop (`while true; do curl -d "$(yes '#' | head -c 1m)" ...; done`) exhausts the single-threaded server and out free-tier CPU quota in seconds. `Content-Length` is honored but uncapped (line 86).
**Fix:** Cap body size; add a simple in-memory token bucket.
```python
MAX_BODY = 64 * 1024  # 64 KiB
# in do_POST:
length = min(int(self.headers.get("Content-Length", 0)), MAX_BODY)
if length >= MAX_BODY:
    self.send(413, json.dumps({"error":"payload too large"})); return

# token bucket dict keyed by client IP, refill 10 req/min
import time, collections
BUCKET = {}
def rate_ok(ip, limit=10, window=60):
    now=time.time(); t=BUCKET.get(ip,[0,0.0])
    if now-t[1] > window: t=[limit, now]
    if t[0] <= 0: return False
    t[0]-=1; BUCKET[ip]=t; return True
# gate do_POST with: if not rate_ok(self.client_address[0]): self.send(429, ...); return
```

### 4. MEDIUM — Unbounded request body / memory DoS
**Description:** `self.rfile.read(length)` (line 87) allocates `length` bytes unbounded. A `Content-Length: 999999999` header OOMs the process. Distinct from rate limiting — even one request wins.
**Fix:** Same `MAX_BODY` cap from §3; reject before reading. Also `decode("utf-8", errors="replace")` is fine but irrelevant once capped.

### 5. MEDIUM — No input validation on JSON path
**Description:** Line 89 calls `json.loads(raw)` then `.get("markdown", raw)` — if JSON has non-string `markdown` (e.g. `{"markdown": 5}`), `md_to_html(5)` blows up mid-request with an unhandled `AttributeError`; in a single-threaded server that returns a 500 with a stack trace (info leak). No `try/except` around `md_to_html`.
**Fix:** Validate type; wrap conversion.
```python
md = json.loads(raw).get("markdown", raw)
if not isinstance(md, str): md = str(md)
try:
    html = md_to_html(md)
except Exception:
    html = ""
self.send(200, json.dumps({"html": html}))
```

### 6. LOW — Verbose error / info leak on parse failure
**Description:** Currently swallowed (line 90 `except Exception: md = raw`), which is safe-ish but silently degrades. The bigger risk: no global request `try/except`, so any unexpected exception yields a default 500 with a Python traceback sent to the client (env paths, library versions). Disable `BaseHTTPRequestHandler` default error pages.
**Fix:** Override `error_response` / wrap `do_GET`, `do_POST` and return a generic `{"error":"internal"}` 500.

## Minimum hardening checklist (before public)
1. **Fix XSS:** escape code-block contents on reinsert and allowlist link href schemes (`http(s)`, `mailto`, relative).
2. **Body cap:** reject `Content-Length > 64KiB` *before* reading; return 413.
3. **Rate limit:** per-IP token bucket, ~10 req/min; return 429. (Use Redis when you go multi-worker.)
4. **CORS hardening:** emit a single explicit `Access-Control-Allow-Origin`; add `X-Content-Type-Options: nosniff` and `Content-Security-Policy: default-src 'none'` on responses.
5. **Front it with a proxy:** bind `127.0.0.1`, put nginx/Caddy in front for TLS, `/health` auth, and DDoS scrubbing.

---
*Re-test after each fix. No auth layer yet — add API keys before any monetization.*
