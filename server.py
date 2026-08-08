<<<<<<< Updated upstream
"""Markdown-to-HTML API server with billing + analytics + security hardening.
Stdlib only. Run: python server.py"""
import http.server, json, re, os, time, threading
from billing import record_call, register_client, FREE_TIER_LIMIT
from analytics import log_call, get_stats, daily_report
from extra_endpoints import HANDLERS as ENDPOINT_HANDLERS  # /json/prettify, /text/stats, /slug

PORT = 8777
VERSION = "1.1.0"  # bumped for hardening pass (health detail, CORS preflight, edge cases)
MAX_BODY = 1024 * 1024  # 1MB body cap (anti-OOM)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # max requests per IP per window
_STARTED_AT = time.time()  # server startup timestamp for /health uptime

# Load real LTC wallet address from wallet.json
_WALLET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallet.json")
try:
    with open(_WALLET_FILE) as _f:
        WALLET_ADDRESS = json.load(_f).get("address", "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM")
except Exception:
    WALLET_ADDRESS = "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"

# --- Rate limiter (thread-safe, in-memory) ---
_rate_lock = threading.Lock()
_rate_map = {}  # {ip: [(timestamp, ...)]}

def rate_check(ip):
    """Return True if IP is within rate limit, False if exceeded."""
    now = time.time()
    with _rate_lock:
        reqs = _rate_map.get(ip, [])
        # Prune old entries
        reqs = [t for t in reqs if now - t < RATE_LIMIT_WINDOW]
        if len(reqs) >= RATE_LIMIT_MAX:
            _rate_map[ip] = reqs
            return False
        reqs.append(now)
        _rate_map[ip] = reqs
        return True

# --- Billing client identity (API key via X-API-Key, else IP) ---
def billing_client_id(handler):
    """Return the billing identifier for this request: the X-API-Key header
    if present, otherwise the client IP. This lets callers behind a shared NAT
    or proxy get their own free-tier bucket by sending an API key."""
    key = handler.headers.get("X-API-Key")
    if key and key.strip():
        return key.strip()
    return handler.client_address[0]

# --- Safe URL validator (prevents javascript: scheme XSS) ---
def safe_url(url):
    """Sanitize URL — block javascript:, data:, vbscript: schemes."""
    u = url.strip().lower()
    if u.startswith(("javascript:", "data:", "vbscript:", "file:")):
        return "#"
    return url

def md_to_html(text):
    """Convert markdown to HTML with XSS-safe escaping."""
    if not isinstance(text, str):
        text = str(text)

    # Extract code blocks first to protect them
    blocks = []
    def save_block(m):
        # Escape code block content BEFORE storing (prevent XSS)
        code = (m.group(2)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
        blocks.append(code)
        return f"\x00CODE{len(blocks)-1}\x00"
    text = re.sub(r"```[ \t]*(\w*)\n(.*?)```", save_block, text, flags=re.DOTALL)

    # Escape HTML in remaining text
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    lines = text.split("\n")
    out, in_list = [], False
    for line in lines:
        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if in_list: out.append("</ul>"); in_list = False
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{m.group(2)}</h{lvl}>")
            continue
        # Unordered list
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{m.group(1)}</li>")
            continue
        if in_list: out.append("</ul>"); in_list = False
        out.append(line)
    if in_list: out.append("</ul>")
    text = "\n".join(out)

    # Inline: bold, italic, links (with safe URL), inline code
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links with URL sanitization
    def safe_link(m):
        url = safe_url(m.group(2))
        return f'<a href="{url}">{m.group(1)}</a>'
    text = re.sub(r"\[(.+?)\]\((.+?)\)", safe_link, text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)

    # Restore code blocks (already escaped)
    for i, code in enumerate(blocks):
        text = text.replace(f"\x00CODE{i}\x00", f"<pre><code>{code}</code></pre>")
    return text.strip()

GUIDE = """Markdown-to-HTML API — Usage Guide
=====================================
GET /register
  Mint a new API key. Returns: {"api_key": "mk_...", "wallet_address": "...",
                                "free_tier_limit": 10, "calls_made": 0, "remaining": 10}
  Send the returned key on every billed request via the X-API-Key header.
  Without a key, billing falls back to your IP address (still 10 free calls).

POST /convert
  Headers: optional X-API-Key: mk_...
  Body: raw markdown text (Content-Type: text/plain or application/json {"markdown": "..."})
  Returns: {"html": "<converted html string>", "billing": {...}}
  Supported: headings, bold, italic, links, inline/block code, unordered lists.
  Free tier: 10 free calls per client (IP or API key). Then 402 + LTC wallet.

POST /json/prettify
  Body: application/json {"json": "<compact JSON string>"}
  Returns: the input JSON re-indented with 2-space pretty printing,
           plus a "billing" object. 400 on invalid JSON.

POST /text/stats
  Body: application/json {"text": "<any text>"}
  Returns: {"words": N, "chars": N, "chars_no_spaces": N,
            "reading_time_min": float, "top_words": [[word, count], ...],
            "billing": {...}}

POST /slug
  Body: application/json {"title": "<title string>"}
  Returns: {"slug": "<url-safe-slug>", "billing": {...}}

GET /health   -> {"status":"ok","version":"...","uptime_seconds":N,"port":8777,...}
GET /docs     -> this guide
GET /payment  -> {"wallet_address": "...", "currency": "LTC"}
GET /usage    -> {"calls_made": N, "remaining": N}
GET /stats    -> {"total_calls": N, "unique_ips": N, ...}

Rate limit: 30 requests/minute per IP. Max body: 1MB.
All POST endpoints share the same free tier (10 free calls per client — IP or API key) and billing.

Examples:
  curl -X POST http://localhost:8777/convert -H "Content-Type: application/json" -d '{"markdown": "# Hello **world**"}'
  curl -X POST http://localhost:8777/json/prettify -H "Content-Type: application/json" -d '{"json":"{\\"a\\":1,\\"b\\":2}"}'
  curl -X POST http://localhost:8777/text/stats -H "Content-Type: application/json" -d '{"text":"The quick brown fox"}'
  curl -X POST http://localhost:8777/slug -H "Content-Type: application/json" -d '{"title":"Café — Menus & Drinks!"}'
  curl http://localhost:8777/health
  curl http://localhost:8777/payment
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        """CORS preflight handler — respond 204 with allow headers, no body."""
        t0 = time.time()
        client_ip = self.client_address[0]
        try:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
            self.send_header("Access-Control-Max-Age", "86400")
            self.end_headers()
            log_call(self.path, client_ip, 204, time.time() - t0)
        except Exception:
            self.send_response(500)
            self.end_headers()
            log_call(self.path, client_ip, 500, time.time() - t0)

    def do_GET(self):
        client_ip = self.client_address[0]
        t0 = time.time()
        try:
            # Rate limit check
            if not rate_check(client_ip):
                self.send(429, json.dumps({"error": "Rate limit exceeded", "retry_after": RATE_LIMIT_WINDOW}))
                log_call(self.path, client_ip, 429, time.time() - t0)
                return

            if self.path == "/health":
                uptime = time.time() - _STARTED_AT
                self.send(200, json.dumps({
                    "status": "ok",
                    "version": VERSION,
                    "uptime_seconds": round(uptime, 1),
                    "uptime": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
                    "port": PORT,
                    "timestamp": int(time.time()),
                    "endpoints": ["/health", "/register", "/convert", "/json/prettify", "/text/stats", "/slug", "/docs", "/payment", "/usage", "/stats"]
                }))
                log_call("/health", client_ip, 200, time.time() - t0)
            elif self.path == "/docs":
                self.send(200, GUIDE, ctype="text/plain")
                log_call("/docs", client_ip, 200, time.time() - t0)
            elif self.path == "/payment":
                self.send(200, json.dumps({
                    "wallet_address": WALLET_ADDRESS,
                    "currency": "LTC",
                    "message": "Send any amount of Litecoin to this address to continue using the API after the free tier."
                }))
                log_call("/payment", client_ip, 200, time.time() - t0)
            elif self.path == "/register":
                # Mint a new API key, keyed independently of the caller's IP so
                # NAT/proxy users get their own free-tier bucket.
                reg = register_client(ip=client_ip)
                self.send(200, json.dumps(reg))
                log_call("/register", client_ip, 200, time.time() - t0)
            elif self.path == "/usage":
                from billing import check_usage
                cid = billing_client_id(self)
                usage = check_usage(cid)
                self.send(200, json.dumps({
                    "client": cid,
                    "calls_made": usage.get("call_count", 0),
                    "free_tier_limit": FREE_TIER_LIMIT,
                    "remaining": max(FREE_TIER_LIMIT - usage.get("call_count", 0), 0)
                }))
                log_call("/usage", client_ip, 200, time.time() - t0)
            elif self.path == "/stats":
                self.send(200, json.dumps(get_stats()))
                log_call("/stats", client_ip, 200, time.time() - t0)
            elif self.path == "/uptime":
                stats = get_stats()
                self.send(200, json.dumps({
                    "uptime_seconds": round(time.time() - _STARTED_AT, 1),
                    "total_calls": stats.get("total_calls", 0),
                    "unique_ips": stats.get("unique_ips", 0),
                }))
                log_call("/uptime", client_ip, 200, time.time() - t0)
            elif self.path == "/" or self.path == "/index.html":
                # Serve the landing page
                idx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
                if os.path.exists(idx):
                    with open(idx) as f:
                        self.send(200, f.read(), ctype="text/html")
                    log_call("/", client_ip, 200, time.time() - t0)
                else:
                    self.send(404, json.dumps({"error": "landing page not found"}))
            else:
                self.send(404, json.dumps({"error": "not found"}))
                log_call(self.path, client_ip, 404, time.time() - t0)
        except Exception as e:
            self.send(500, json.dumps({"error": "internal server error"}))
            log_call(self.path, client_ip, 500, time.time() - t0)

    # JSON body field name expected by each extra endpoint.
    _EXTRA_BODY_FIELD = {
        "/json/prettify": "json",
        "/text/stats": "text",
        "/slug": "title",
    }

    def _read_body(self):
        """Read and enforce the body cap. Returns (raw_str, error_json_str) or
        (None, 404) if no Content-Length. On failure error_json_str is set and
        raw is None. Caller must log the supplied status."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return None, 400, json.dumps({"error": "Invalid Content-Length"})
        if length <= 0:
            return None, 400, json.dumps({"error": "Empty request body",
                                          "message": "POST a non-empty body. See /docs for usage."})
        if length > MAX_BODY:
            return None, 413, json.dumps({"error": "Request body too large",
                                          "max_bytes": MAX_BODY,
                                          "message": f"Body exceeds the {MAX_BODY}-byte limit."})
        return self.rfile.read(length).decode("utf-8", errors="replace"), 200, None

    def do_POST(self):
        client_ip = self.client_address[0]
        t0 = time.time()
        path = self.path
        try:
            # Rate limit check
            if not rate_check(client_ip):
                self.send(429, json.dumps({"error": "Rate limit exceeded", "retry_after": RATE_LIMIT_WINDOW}))
                log_call(path, client_ip, 429, time.time() - t0)
                return

            # ---- /convert: markdown -> HTML ---------------------------------
            if path == "/convert":
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                # /convert-specific body cap: 50KB markdown input
                if len(raw) > 50 * 1024:
                    self.send(413, json.dumps({
                        "error": "Markdown input too large",
                        "max_bytes": 50 * 1024,
                        "received_bytes": len(raw),
                        "message": "Markdown input exceeds the 50KB limit. Truncate and retry."
                    }))
                    log_call(path, client_ip, 413, time.time() - t0)
                    return
                # Billing check (only after body validation)
                bill = record_call(billing_client_id(self))
                if bill.get("status") == 402:
                    self.send(402, json.dumps(bill))
                    log_call(path, client_ip, 402, time.time() - t0)
                    return
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        md = json.loads(raw).get("markdown", raw)
                        if not isinstance(md, str):
                            md = str(md)
                    except Exception:
                        md = raw
                else:
                    md = raw
                if md is None or (isinstance(md, str) and md.strip() == ""):
                    self.send(200, json.dumps({
                        "html": "",
                        "warning": "Empty markdown input — no HTML generated.",
                        "billing": bill
                    }))
                    log_call(path, client_ip, 200, time.time() - t0)
                    return
                html = md_to_html(md)
                self.send(200, json.dumps({"html": html, "billing": bill}))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # ---- extra endpoints: /json/prettify, /text/stats, /slug --------
            if path in ENDPOINT_HANDLERS:
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                # Billing check
                bill = record_call(billing_client_id(self))
                if bill.get("status") == 402:
                    self.send(402, json.dumps(bill))
                    log_call(path, client_ip, 402, time.time() - t0)
                    return
                # Extract the named field from a JSON body, fall back to raw.
                field = self._EXTRA_BODY_FIELD.get(path, "text")
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        body_text = json.loads(raw).get(field, raw)
                        if not isinstance(body_text, str):
                            body_text = str(body_text)
                    except Exception:
                        body_text = raw
                else:
                    body_text = raw
                if body_text is None or body_text.strip() == "":
                    self.send(400, json.dumps({
                        "error": f"Empty '{field}' field",
                        "message": f"POST a JSON object with a non-empty '{field}' string. See /docs for usage."
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                try:
                    result = ENDPOINT_HANDLERS[path](body_text)
                except ValueError as ve:
                    self.send(400, json.dumps({"error": "Bad input", "message": str(ve)}))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                # /slug returns a bare slug; the others return JSON objects.
                if path == "/slug":
                    self.send(200, json.dumps({"slug": result, "billing": bill}))
                else:
                    # Wrap the handler's JSON string back into an object so we
                    # can attach billing uniformly.
                    obj = json.loads(result)
                    obj["billing"] = bill
                    self.send(200, json.dumps(obj, ensure_ascii=False))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # Unknown POST path
            self.send(404, json.dumps({"error": "not found"}))
            log_call(path, client_ip, 404, time.time() - t0)
        except Exception:
            self.send(500, json.dumps({"error": "internal server error"}))
            log_call(path, client_ip, 500, time.time() - t0)

if __name__ == "__main__":
    print(f"Markdown-to-HTML API on http://0.0.0.0:{PORT}")
    print(f"  Rate limit: {RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s per IP")
    print(f"  Body cap: {MAX_BODY} bytes")
    print(f"  Free tier: {FREE_TIER_LIMIT} calls, then 402 + LTC")
    # Threaded server for better DoS resistance
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
=======
"""Markdown-to-HTML API server with billing + analytics + security hardening.
Stdlib only. Run: python server.py"""
import http.server, json, re, os, time, threading
from billing import record_call, register_client, FREE_TIER_LIMIT
from analytics import log_call, get_stats, daily_report
from extra_endpoints import HANDLERS as ENDPOINT_HANDLERS  # /json/prettify, /text/stats, /slug

PORT = 8777
VERSION = "1.2.0"  # bumped for /batch + /sanitize endpoints
MAX_BODY = 1024 * 1024  # 1MB body cap (anti-OOM)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # max requests per IP per window
BATCH_MAX_ITEMS = 50  # max items per /batch request
_STARTED_AT = time.time()  # server startup timestamp for /health uptime

# Load real LTC wallet address from wallet.json
_WALLET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallet.json")
try:
    with open(_WALLET_FILE) as _f:
        WALLET_ADDRESS = json.load(_f).get("address", "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM")
except Exception:
    WALLET_ADDRESS = "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"

# --- Rate limiter (thread-safe, in-memory) ---
_rate_lock = threading.Lock()
_rate_map = {}  # {ip: [(timestamp, ...)]}

def rate_check(ip):
    """Return True if IP is within rate limit, False if exceeded."""
    now = time.time()
    with _rate_lock:
        reqs = _rate_map.get(ip, [])
        # Prune old entries
        reqs = [t for t in reqs if now - t < RATE_LIMIT_WINDOW]
        if len(reqs) >= RATE_LIMIT_MAX:
            _rate_map[ip] = reqs
            return False
        reqs.append(now)
        _rate_map[ip] = reqs
        return True

# --- Billing client identity (API key via X-API-Key, else IP) ---
def billing_client_id(handler):
    """Return the billing identifier for this request: the X-API-Key header
    if present, otherwise the client IP. This lets callers behind a shared NAT
    or proxy get their own free-tier bucket by sending an API key."""
    key = handler.headers.get("X-API-Key")
    if key and key.strip():
        return key.strip()
    return handler.client_address[0]

# --- Safe URL validator (prevents javascript: scheme XSS) ---
def safe_url(url):
    """Sanitize URL — block javascript:, data:, vbscript: schemes."""
    u = url.strip().lower()
    if u.startswith(("javascript:", "data:", "vbscript:", "file:")):
        return "#"
    return url

def sanitize_markdown(text):
    """Escape raw HTML in markdown (< > &) so md_to_html converts only markup.

    This is a pre-conversion pass: any literal '<', '>', '&' in the source
    markdown are turned into their HTML-entity equivalents BEFORE the converter
    runs, so embedded raw HTML tags are rendered as visible text rather than
    interpreted as markup. Code fences (```...```) are preserved as markdown so
    that md_to_html still wraps them in <pre><code> blocks with their own
    escaping.
    """
    if not isinstance(text, str):
        text = str(text)
    # Protect fenced code blocks so we don't double-escape their delimiters
    blocks = []
    def _save_block(m):
        blocks.append(m.group(0))
        return f"\x00RAWCODE{len(blocks) - 1}\x00"
    text = re.sub(r"```[ \t]*(\w*)\n.*?```", _save_block, text, flags=re.DOTALL)
    # Escape raw HTML characters in the surrounding markdown
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
    # Restore fenced code blocks untouched (md_to_html will escape their contents)
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00RAWCODE{i}\x00", block)
    return text


def md_to_html(text, already_escaped=False):
    """Convert markdown to HTML with XSS-safe escaping.

    If already_escaped is True, the caller has already escaped raw HTML
    characters (< > &) in the surrounding text, so we skip our own
    escape pass to avoid double-escaping. Code-block contents are always
    escaped regardless (they are extracted and re-escaped by save_block).
    """
    if not isinstance(text, str):
        text = str(text)

    # Extract code blocks first to protect them
    blocks = []
    def save_block(m):
        # Escape code block content BEFORE storing (prevent XSS)
        code = (m.group(2)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
        blocks.append(code)
        return f"\x00CODE{len(blocks)-1}\x00"
    text = re.sub(r"```[ \t]*(\w*)\n(.*?)```", save_block, text, flags=re.DOTALL)

    # Escape HTML in remaining text (skip if caller already pre-escaped)
    if not already_escaped:
        text = (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))

    lines = text.split("\n")
    out, in_list = [], False
    for line in lines:
        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if in_list: out.append("</ul>"); in_list = False
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{m.group(2)}</h{lvl}>")
            continue
        # Unordered list
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{m.group(1)}</li>")
            continue
        if in_list: out.append("</ul>"); in_list = False
        out.append(line)
    if in_list: out.append("</ul>")
    text = "\n".join(out)

    # Inline: bold, italic, links (with safe URL), inline code
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Links with URL sanitization
    def safe_link(m):
        url = safe_url(m.group(2))
        return f'<a href="{url}">{m.group(1)}</a>'
    text = re.sub(r"\[(.+?)\]\((.+?)\)", safe_link, text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)

    # Restore code blocks (already escaped)
    for i, code in enumerate(blocks):
        text = text.replace(f"\x00CODE{i}\x00", f"<pre><code>{code}</code></pre>")
    return text.strip()

GUIDE = """Markdown-to-HTML API — Usage Guide
=====================================
GET /register
  Mint a new API key. Returns: {"api_key": "mk_...", "wallet_address": "...",
                                "free_tier_limit": 10, "calls_made": 0, "remaining": 10}
  Send the returned key on every billed request via the X-API-Key header.
  Without a key, billing falls back to your IP address (still 10 free calls).

POST /convert
  Headers: optional X-API-Key: ***
  Body: raw markdown text (Content-Type: text/plain or application/json {"markdown": "..."})
  Returns: {"html": "<converted html string>", "billing": {...}}
  Supported: headings, bold, italic, links, inline/block code, unordered lists.
  Free tier: 10 free calls per client (IP or API key). Then 402 + LTC wallet.

POST /sanitize
  Headers: optional X-API-Key: ***
  Body: raw markdown text (Content-Type: text/plain or application/json {"markdown": "..."})
  Strips raw HTML from markdown (escapes < > &) BEFORE converting to HTML.
  Returns: {"html": "<sanitized html>", "sanitized": true, "billing": {...}}
  Use this when the source markdown may contain untrusted raw HTML that should
  be rendered as literal text rather than interpreted as markup.

POST /batch
  Headers: optional X-API-Key: ***
  Body: application/json {"items": ["md1", "md2", ...]}  (max 50 items)
  Returns: {"results": ["html1", "html2", ...], "count": N, "billing": {...}}
  Converts up to 50 markdown strings in one request. Billed per item
  (1 billing call per item in the batch). If the free tier is exhausted mid-batch,
  returns 402 with the partial_results converted so far.

POST /json/prettify
  Body: application/json {"json": "<compact JSON string>"}
  Returns: the input JSON re-indented with 2-space pretty printing,
           plus a "billing" object. 400 on invalid JSON.

POST /text/stats
  Body: application/json {"text": "<any text>"}
  Returns: {"words": N, "chars": N, "chars_no_spaces": N,
            "reading_time_min": float, "top_words": [[word, count], ...],
            "billing": {...}}

POST /slug
  Body: application/json {"title": "<title string>"}
  Returns: {"slug": "<url-safe-slug>", "billing": {...}}

GET /health   -> {"status":"ok","version":"...","uptime_seconds":N,"port":8777,...}
GET /docs     -> this guide
GET /pricing  -> {"free_tier": {...}, "paid_tier": {...}, "rate_limit": {...}}
GET /payment  -> {"wallet_address": "...", "currency": "LTC"}
GET /usage    -> {"calls_made": N, "remaining": N}
GET /stats    -> {"total_calls": N, "unique_ips": N, ...}

Rate limit: 30 requests/minute per IP. Max body: 1MB.
All POST endpoints share the same free tier (10 free calls per client — IP or API key) and billing.

Examples:
  curl -X POST http://localhost:8777/convert -H "Content-Type: application/json" -d '{"markdown": "# Hello **world**"}'
  curl -X POST http://localhost:8777/sanitize -H "Content-Type: application/json" -d '{"markdown": "# Hi <script>alert(1)</script>"}'
  curl -X POST http://localhost:8777/batch -H "Content-Type: application/json" -d '{"items": ["# A", "## B"]}'
  curl -X POST http://localhost:8777/json/prettify -H "Content-Type: application/json" -d '{"json":"{\"a\":1,\"b\":2}"}'
  curl -X POST http://localhost:8777/text/stats -H "Content-Type: application/json" -d '{"text":"The quick brown fox"}'
  curl -X POST http://localhost:8777/slug -H "Content-Type: application/json" -d '{"title":"Café — Menus & Drinks!"}'
  curl http://localhost:8777/health
  curl http://localhost:8777/payment
"""

SWAGGER_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "MD2HTML API",
        "description": "Markdown-to-HTML conversion API with JSON/text utilities, billing, and analytics. Free tier: 10 calls per client (IP or X-API-Key), then HTTP 402 + LTC payment. Stdlib-only Python server.",
        "version": VERSION,
        "contact": {"url": "https://github.com/dcn13l/md2html-api"},
    },
    "servers": [
        {"url": "http://147.15.103.217/md2html", "description": "Production VPS"},
        {"url": "http://localhost:8777", "description": "Local development"},
    ],
    "components": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Optional — obtained from GET /register. Without it, billing falls back to client IP."
            }
        },
        "schemas": {
            "Billing": {
                "type": "object",
                "properties": {
                    "status": {"type": "integer", "example": 200},
                    "calls_made": {"type": "integer"},
                    "remaining": {"type": "integer"},
                    "free_tier_limit": {"type": "integer", "example": 10},
                },
            },
            "PaymentRequired": {
                "type": "object",
                "properties": {
                    "status": {"type": "integer", "example": 402},
                    "error": {"type": "string", "example": "Payment Required"},
                    "message": {"type": "string"},
                    "wallet_address": {"type": "string"},
                    "calls_made": {"type": "integer"},
                    "free_tier_limit": {"type": "integer"},
                },
            },
            "RateLimited": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Rate limit exceeded"},
                    "retry_after": {"type": "integer"},
                },
            },
            "ConvertResponse": {
                "type": "object",
                "properties": {
                    "html": {"type": "string"},
                    "billing": {"$ref": "#/components/schemas/Billing"},
                    "warning": {"type": "string"},
                },
            },
            "JsonPrettifyResponse": {
                "type": "object",
                "description": "Pretty-printed JSON object (dynamic fields) with a 'billing' key added.",
            },
            "TextStats": {
                "type": "object",
                "properties": {
                    "words": {"type": "integer"},
                    "chars": {"type": "integer"},
                    "chars_no_spaces": {"type": "integer"},
                    "reading_time_min": {"type": "number"},
                    "top_words": {
                        "type": "array",
                        "items": {"type": "array", "items": {"oneOf": [{"type": "string"}, {"type": "integer"}]}},
                    },
                    "billing": {"$ref": "#/components/schemas/Billing"},
                },
            },
            "SlugResponse": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "example": "hello-world"},
                    "billing": {"$ref": "#/components/schemas/Billing"},
                },
            },
            "SanitizeResponse": {
                "type": "object",
                "properties": {
                    "html": {"type": "string"},
                    "sanitized": {"type": "boolean", "example": True},
                    "billing": {"$ref": "#/components/schemas/Billing"},
                },
            },
            "BatchResponse": {
                "type": "object",
                "properties": {
                    "results": {"type": "array", "items": {"type": "string"}},
                    "count": {"type": "integer"},
                    "billing": {"$ref": "#/components/schemas/Billing"},
                },
            },
        },
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "responses": {"200": {"description": "Server status", "content": {"application/json": {"schema": {"type": "object"}}}}},
            }
        },
        "/register": {
            "get": {
                "summary": "Mint a new API key",
                "responses": {"200": {"description": "New API key + wallet info", "content": {"application/json": {"schema": {"type": "object", "properties": {"api_key": {"type": "string"}, "wallet_address": {"type": "string"}, "free_tier_limit": {"type": "integer"}, "calls_made": {"type": "integer"}, "remaining": {"type": "integer"}}}}}}},
            }
        },
        "/convert": {
            "post": {
                "summary": "Convert Markdown to HTML",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "text/plain": {"schema": {"type": "string"}},
                        "application/json": {"schema": {"type": "object", "properties": {"markdown": {"type": "string"}}}},
                    },
                },
                "responses": {
                    "200": {"description": "Converted HTML", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ConvertResponse"}}}},
                    "402": {"description": "Free tier exhausted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                    "429": {"description": "Rate limited", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RateLimited"}}}},
                },
            }
        },
        "/sanitize": {
            "post": {
                "summary": "Strip raw HTML from markdown, then convert to HTML",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "text/plain": {"schema": {"type": "string"}},
                        "application/json": {"schema": {"type": "object", "properties": {"markdown": {"type": "string"}}}},
                    },
                },
                "responses": {
                    "200": {"description": "Sanitized HTML", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SanitizeResponse"}}}},
                    "402": {"description": "Free tier exhausted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                    "429": {"description": "Rate limited", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RateLimited"}}}},
                },
            }
        },
        "/batch": {
            "post": {
                "summary": "Convert up to 50 markdown strings to HTML in one request",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "string"}, "maxItems": 50}}}}},
                },
                "responses": {
                    "200": {"description": "Batch conversion results", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BatchResponse"}}}},
                    "400": {"description": "Invalid body (missing items, not a list, empty, null item)"},
                    "402": {"description": "Free tier exhausted mid-batch (partial_results included)", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                    "413": {"description": "Too many items (max 50)"},
                    "429": {"description": "Rate limited", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RateLimited"}}}},
                },
            }
        },
        "/json/prettify": {
            "post": {
                "summary": "Pretty-print compact JSON",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"json": {"type": "string"}}}}}},
                "responses": {
                    "200": {"description": "Pretty-printed JSON", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/JsonPrettifyResponse"}}}},
                    "400": {"description": "Invalid JSON"},
                    "402": {"description": "Free tier exhausted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                },
            }
        },
        "/text/stats": {
            "post": {
                "summary": "Compute text statistics",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"text": {"type": "string"}}}}}},
                "responses": {
                    "200": {"description": "Text stats", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TextStats"}}}},
                    "402": {"description": "Free tier exhausted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                },
            }
        },
        "/slug": {
            "post": {
                "summary": "Generate a URL-safe slug",
                "security": [{"ApiKeyAuth": []}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"title": {"type": "string"}}}}}},
                "responses": {
                    "200": {"description": "URL-safe slug", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SlugResponse"}}}},
                    "402": {"description": "Free tier exhausted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PaymentRequired"}}}},
                },
            }
        },
        "/docs": {
            "get": {
                "summary": "Plain-text usage guide",
                "responses": {"200": {"description": "Usage guide", "content": {"text/plain": {"schema": {"type": "string"}}}}},
            }
        },
        "/pricing": {
            "get": {
                "summary": "Pricing tiers and rate limits",
                "responses": {"200": {"description": "Pricing info", "content": {"application/json": {"schema": {"type": "object"}}}}},
            }
        },
        "/payment": {
            "get": {
                "summary": "LTC wallet address for payment",
                "responses": {"200": {"description": "Payment info", "content": {"application/json": {"schema": {"type": "object", "properties": {"wallet_address": {"type": "string"}, "currency": {"type": "string", "example": "LTC"}}}}}}},
            }
        },
        "/usage": {
            "get": {
                "summary": "Check current client usage",
                "security": [{"ApiKeyAuth": []}],
                "responses": {"200": {"description": "Usage stats for this client", "content": {"application/json": {"schema": {"type": "object"}}}}},
            }
        },
        "/stats": {
            "get": {
                "summary": "Global analytics stats",
                "responses": {"200": {"description": "Server-wide analytics", "content": {"application/json": {"schema": {"type": "object"}}}}},
            }
        },
        "/swagger.json": {
            "get": {
                "summary": "OpenAPI 3.0 specification",
                "responses": {"200": {"description": "OpenAPI spec", "content": {"application/json": {"schema": {"type": "object"}}}}},
            }
        },
    },
}


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        """CORS preflight handler — respond 204 with allow headers, no body."""
        t0 = time.time()
        client_ip = self.client_address[0]
        try:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key")
            self.send_header("Access-Control-Max-Age", "86400")
            self.end_headers()
            log_call(self.path, client_ip, 204, time.time() - t0)
        except Exception:
            self.send_response(500)
            self.end_headers()
            log_call(self.path, client_ip, 500, time.time() - t0)

    def do_GET(self):
        client_ip = self.client_address[0]
        t0 = time.time()
        try:
            # Rate limit check
            if not rate_check(client_ip):
                self.send(429, json.dumps({"error": "Rate limit exceeded", "retry_after": RATE_LIMIT_WINDOW}))
                log_call(self.path, client_ip, 429, time.time() - t0)
                return

            if self.path == "/health":
                uptime = time.time() - _STARTED_AT
                self.send(200, json.dumps({
                    "status": "ok",
                    "version": VERSION,
                    "uptime_seconds": round(uptime, 1),
                    "uptime": f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
                    "port": PORT,
                    "timestamp": int(time.time()),
                    "endpoints": ["/health", "/register", "/convert", "/sanitize", "/batch", "/json/prettify", "/text/stats", "/slug", "/docs", "/pricing", "/payment", "/usage", "/stats"]
                }))
                log_call("/health", client_ip, 200, time.time() - t0)
            elif self.path == "/swagger.json":
                self.send(200, json.dumps(SWAGGER_SPEC, indent=2, ensure_ascii=False))
                log_call("/swagger.json", client_ip, 200, time.time() - t0)
            elif self.path == "/docs":
                self.send(200, GUIDE, ctype="text/plain")
                log_call("/docs", client_ip, 200, time.time() - t0)
            elif self.path == "/pricing":
                # Pricing stub — public plan info; no auth/billing.
                self.send(200, json.dumps({
                    "free_tier": {
                        "calls": FREE_TIER_LIMIT,
                        "price_per_call": "0.00 USD",
                        "auth": "none — identified by IP or X-API-Key"
                    },
                    "paid_tier": {
                        "price_per_call": "0.001 USD",
                        "currency": "LTC",
                        "wallet_address": WALLET_ADDRESS,
                        "note": "Send Litecoin to the wallet to continue after the free tier."
                    },
                    "rate_limit": {"max": RATE_LIMIT_MAX, "window_seconds": RATE_LIMIT_WINDOW},
                    "max_body_bytes": MAX_BODY
                }))
                log_call("/pricing", client_ip, 200, time.time() - t0)
            elif self.path == "/payment":
                self.send(200, json.dumps({
                    "wallet_address": WALLET_ADDRESS,
                    "currency": "LTC",
                    "message": "Send any amount of Litecoin to this address to continue using the API after the free tier."
                }))
                log_call("/payment", client_ip, 200, time.time() - t0)
            elif self.path == "/register":
                # Mint a new API key, keyed independently of the caller's IP so
                # NAT/proxy users get their own free-tier bucket.
                reg = register_client(ip=client_ip)
                self.send(200, json.dumps(reg))
                log_call("/register", client_ip, 200, time.time() - t0)
            elif self.path == "/usage":
                from billing import check_usage
                cid = billing_client_id(self)
                usage = check_usage(cid)
                self.send(200, json.dumps({
                    "client": cid,
                    "calls_made": usage.get("call_count", 0),
                    "free_tier_limit": FREE_TIER_LIMIT,
                    "remaining": max(FREE_TIER_LIMIT - usage.get("call_count", 0), 0)
                }))
                log_call("/usage", client_ip, 200, time.time() - t0)
            elif self.path == "/stats":
                self.send(200, json.dumps(get_stats()))
                log_call("/stats", client_ip, 200, time.time() - t0)
            elif self.path == "/uptime":
                stats = get_stats()
                self.send(200, json.dumps({
                    "uptime_seconds": round(time.time() - _STARTED_AT, 1),
                    "total_calls": stats.get("total_calls", 0),
                    "unique_ips": stats.get("unique_ips", 0),
                }))
                log_call("/uptime", client_ip, 200, time.time() - t0)
            elif self.path == "/" or self.path == "/index.html":
                # Serve the landing page
                idx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
                if os.path.exists(idx):
                    with open(idx) as f:
                        self.send(200, f.read(), ctype="text/html")
                    log_call("/", client_ip, 200, time.time() - t0)
                else:
                    self.send(404, json.dumps({"error": "landing page not found"}))
            else:
                self.send(404, json.dumps({"error": "not found"}))
                log_call(self.path, client_ip, 404, time.time() - t0)
        except Exception as e:
            self.send(500, json.dumps({"error": "internal server error"}))
            log_call(self.path, client_ip, 500, time.time() - t0)

    # JSON body field name expected by each extra endpoint.
    _EXTRA_BODY_FIELD = {
        "/json/prettify": "json",
        "/text/stats": "text",
        "/slug": "title",
    }

    def _read_body(self):
        """Read and enforce the body cap. Returns (raw_str, error_json_str) or
        (None, 404) if no Content-Length. On failure error_json_str is set and
        raw is None. Caller must log the supplied status."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return None, 400, json.dumps({"error": "Invalid Content-Length"})
        if length <= 0:
            return None, 400, json.dumps({"error": "Empty request body",
                                          "message": "POST a non-empty body. See /docs for usage."})
        if length > MAX_BODY:
            return None, 413, json.dumps({"error": "Request body too large",
                                          "max_bytes": MAX_BODY,
                                          "message": f"Body exceeds the {MAX_BODY}-byte limit."})
        return self.rfile.read(length).decode("utf-8", errors="replace"), 200, None

    def do_POST(self):
        client_ip = self.client_address[0]
        t0 = time.time()
        path = self.path
        try:
            # Rate limit check
            if not rate_check(client_ip):
                self.send(429, json.dumps({"error": "Rate limit exceeded", "retry_after": RATE_LIMIT_WINDOW}))
                log_call(path, client_ip, 429, time.time() - t0)
                return

            # ---- /convert: markdown -> HTML ---------------------------------
            if path == "/convert":
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                # /convert-specific body cap: 50KB markdown input
                if len(raw) > 50 * 1024:
                    self.send(413, json.dumps({
                        "error": "Markdown input too large",
                        "max_bytes": 50 * 1024,
                        "received_bytes": len(raw),
                        "message": "Markdown input exceeds the 50KB limit. Truncate and retry."
                    }))
                    log_call(path, client_ip, 413, time.time() - t0)
                    return
                # Billing check (only after body validation)
                bill = record_call(billing_client_id(self))
                if bill.get("status") == 402:
                    self.send(402, json.dumps(bill))
                    log_call(path, client_ip, 402, time.time() - t0)
                    return
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        md = json.loads(raw).get("markdown", raw)
                        if not isinstance(md, str):
                            md = str(md)
                    except Exception:
                        md = raw
                else:
                    md = raw
                if md is None or (isinstance(md, str) and md.strip() == ""):
                    self.send(200, json.dumps({
                        "html": "",
                        "warning": "Empty markdown input — no HTML generated.",
                        "billing": bill
                    }))
                    log_call(path, client_ip, 200, time.time() - t0)
                    return
                html = md_to_html(md)
                self.send(200, json.dumps({"html": html, "billing": bill}))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # ---- /sanitize: strip raw HTML, then convert -------------------
            if path == "/sanitize":
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                if len(raw) > 50 * 1024:
                    self.send(413, json.dumps({
                        "error": "Markdown input too large",
                        "max_bytes": 50 * 1024,
                        "received_bytes": len(raw),
                        "message": "Markdown input exceeds the 50KB limit. Truncate and retry."
                    }))
                    log_call(path, client_ip, 413, time.time() - t0)
                    return
                # Billing check (only after body validation)
                bill = record_call(billing_client_id(self))
                if bill.get("status") == 402:
                    self.send(402, json.dumps(bill))
                    log_call(path, client_ip, 402, time.time() - t0)
                    return
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        md = json.loads(raw).get("markdown", raw)
                        if not isinstance(md, str):
                            md = str(md)
                    except Exception:
                        md = raw
                else:
                    md = raw
                if md is None or (isinstance(md, str) and md.strip() == ""):
                    self.send(200, json.dumps({
                        "html": "",
                        "warning": "Empty markdown input — no HTML generated.",
                        "billing": bill
                    }))
                    log_call(path, client_ip, 200, time.time() - t0)
                    return
                clean = sanitize_markdown(md)
                html = md_to_html(clean, already_escaped=True)
                self.send(200, json.dumps({
                    "html": html,
                    "sanitized": True,
                    "billing": bill
                }))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # ---- /batch: convert up to 50 markdown items ------------------
            if path == "/batch":
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                # Parse JSON body
                try:
                    payload = json.loads(raw)
                except Exception:
                    self.send(400, json.dumps({
                        "error": "Invalid JSON",
                        "message": "POST application/json {\"items\": [\"md1\", \"md2\", ...]}"
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                if not isinstance(payload, dict) or "items" not in payload:
                    self.send(400, json.dumps({
                        "error": "Missing 'items' field",
                        "message": "POST {\"items\": [\"md1\", \"md2\", ...]}"
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                items = payload["items"]
                if not isinstance(items, list):
                    self.send(400, json.dumps({
                        "error": "'items' must be a list",
                        "message": "POST {\"items\": [\"md1\", \"md2\", ...]}"
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                if len(items) == 0:
                    self.send(400, json.dumps({
                        "error": "Empty 'items' list",
                        "message": "POST at least one markdown string."
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                if len(items) > BATCH_MAX_ITEMS:
                    self.send(413, json.dumps({
                        "error": "Too many items",
                        "max_items": BATCH_MAX_ITEMS,
                        "received": len(items),
                        "message": f"Batch exceeds the {BATCH_MAX_ITEMS}-item limit."
                    }))
                    log_call(path, client_ip, 413, time.time() - t0)
                    return
                # Coerce non-string items to strings; reject None
                norm = []
                for i, it in enumerate(items):
                    if it is None:
                        self.send(400, json.dumps({
                            "error": f"Item {i} is null",
                            "message": "All items must be strings."
                        }))
                        log_call(path, client_ip, 400, time.time() - t0)
                        return
                    norm.append(it if isinstance(it, str) else str(it))
                # Billing: one record_call per item. A 402 on any item halts the
                # batch and returns the payment-required response for that item.
                cid = billing_client_id(self)
                results = []
                last_bill = None
                for md in norm:
                    bill_i = record_call(cid)
                    last_bill = bill_i
                    if bill_i.get("status") == 402:
                        self.send(402, json.dumps({
                            "error": "Payment Required",
                            "message": (
                                f"Free tier limit exceeded at item {len(results)} "
                                f"of {len(norm)}. Send payment to continue."
                            ),
                            "partial_results": results,
                            "billing": bill_i,
                            "wallet_address": WALLET_ADDRESS,
                        }))
                        log_call(path, client_ip, 402, time.time() - t0)
                        return
                    results.append(md_to_html(md))
                self.send(200, json.dumps({
                    "results": results,
                    "count": len(results),
                    "billing": last_bill
                }))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # ---- extra endpoints: /json/prettify, /text/stats, /slug --------
            if path in ENDPOINT_HANDLERS:
                raw, status, err = self._read_body()
                if raw is None:
                    self.send(status, err)
                    log_call(path, client_ip, status, time.time() - t0)
                    return
                # Billing check
                bill = record_call(billing_client_id(self))
                if bill.get("status") == 402:
                    self.send(402, json.dumps(bill))
                    log_call(path, client_ip, 402, time.time() - t0)
                    return
                # Extract the named field from a JSON body, fall back to raw.
                field = self._EXTRA_BODY_FIELD.get(path, "text")
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        body_text = json.loads(raw).get(field, raw)
                        if not isinstance(body_text, str):
                            body_text = str(body_text)
                    except Exception:
                        body_text = raw
                else:
                    body_text = raw
                if body_text is None or body_text.strip() == "":
                    self.send(400, json.dumps({
                        "error": f"Empty '{field}' field",
                        "message": f"POST a JSON object with a non-empty '{field}' string. See /docs for usage."
                    }))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                try:
                    result = ENDPOINT_HANDLERS[path](body_text)
                except ValueError as ve:
                    self.send(400, json.dumps({"error": "Bad input", "message": str(ve)}))
                    log_call(path, client_ip, 400, time.time() - t0)
                    return
                if path == "/slug":
                    print(f"DEBUG /slug: body_text={repr(body_text)}", flush=True)
                    print(f"DEBUG /slug: result={repr(result)}", flush=True)
                    self.send(200, json.dumps({"slug": result, "billing": bill}))
                else:
                    # Wrap the handler's JSON string back into an object so we
                    # can attach billing uniformly.
                    obj = json.loads(result)
                    obj["billing"] = bill
                    self.send(200, json.dumps(obj, ensure_ascii=False))
                log_call(path, client_ip, 200, time.time() - t0)
                return

            # Unknown POST path
            self.send(404, json.dumps({"error": "not found"}))
            log_call(path, client_ip, 404, time.time() - t0)
        except Exception:
            self.send(500, json.dumps({"error": "internal server error"}))
            log_call(path, client_ip, 500, time.time() - t0)

if __name__ == "__main__":
    print(f"Markdown-to-HTML API on http://0.0.0.0:{PORT}")
    print(f"  Rate limit: {RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s per IP")
    print(f"  Body cap: {MAX_BODY} bytes")
    print(f"  Free tier: {FREE_TIER_LIMIT} calls, then 402 + LTC")
    # Threaded server for better DoS resistance
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
>>>>>>> Stashed changes
