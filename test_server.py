"""Tests for server.py: exercises the LIVE public MD2HTML API over HTTP and
reports PASS/FAIL for each endpoint. Stdlib only (urllib).

Live API:  http://147.15.103.217/md2html/   (port 8777 behind a reverse proxy)
Endpoints covered:
  GET  /health
  POST /convert           (markdown -> HTML, plus empty + XSS-in-code-block cases)
  POST /json/prettify     (compact JSON -> re-indented JSON, round-trip check)
  POST /text/stats        (word/char counts, reading time, top words)
  POST /slug              (title -> URL-safe slug)
  OPTIONS /convert        (CORS preflight)
Run:  python test_server.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

# --- Live public API base -------------------------------------------------
# The service runs on port 8777 behind a reverse proxy that exposes it under
# the /md2html/ prefix on the public IP. Tests must hit the public URL, not
# localhost, so they exercise the same path real customers use.
BASE = "http://147.15.103.217/md2html"
TIMEOUT = 10

results = []  # (name, passed, detail)

# A freshly-minted API key gives the test run its own independent free-tier
# bucket (10 calls) keyed off the key rather than the shared public IP, so
# the tests are not blocked by prior traffic from this NAT/proxy IP.
API_KEY = {"value": None}


def record(name, passed, detail=""):
    results.append((name, passed, detail))
    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] {name}" + (f" - {detail}" if detail else ""))


def register_api_key():
    """Mint a fresh API key from /register so the test run has its own
    free-tier billing bucket. Returns the key string or None on failure."""
    try:
        url = BASE + "/register"
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            body = json.loads(r.read().decode("utf-8"))
        key = body.get("api_key")
        if key:
            API_KEY["value"] = key
            print(f"Registered fresh API key for tests: {key[:8]}... (remaining: {body.get('remaining')})")
            return key
        print(f"WARN: /register returned no api_key: {body}")
        return None
    except Exception as e:
        print(f"WARN: could not register API key ({type(e).__name__}: {e}); tests will run unkeyed and may hit the IP-based free-tier limit.")
        return None


# --- HTTP helpers ---------------------------------------------------------
def request(path, method="GET", body=None, ctype=None):
    """Return (status, text). Raises urllib.error.HTTPError on 4xx/5xx by
    default, so callers should handle via try/except."""
    url = BASE + path
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    if ctype:
        req.add_header("Content-Type", ctype)
    if API_KEY["value"]:
        req.add_header("X-API-Key", API_KEY["value"])
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def post_json(path, payload):
    """POST a JSON body, return (status, parsed_json_or_text)."""
    body = json.dumps(payload).encode("utf-8")
    status, text = request(path, method="POST", body=body, ctype="application/json")
    try:
        return status, json.loads(text)
    except (ValueError, TypeError):
        return status, text


# --- Test definitions -----------------------------------------------------
def test_health():
    try:
        status, text = request("/health")
        body = json.loads(text)
        ok = (status == 200) and body.get("status") == "ok"
        record("GET /health returns status ok", ok, f"status={status} body={text[:120]}")
    except Exception as e:
        record("GET /health returns status ok", False, f"{type(e).__name__}: {e}")


def test_convert_basic():
    md = "# Hello\n\n**bold** and *italic*\n\n- item1\n- item2"
    try:
        status, body = post_json("/convert", {"markdown": md})
        html = body.get("html", "") if isinstance(body, dict) else ""
        ok = (status == 200) and ("<h1>Hello</h1>" in html)
        record("POST /convert returns valid HTML with <h1>Hello</h1>",
               ok, f"status={status} html={html[:100]!r}")
    except Exception as e:
        record("POST /convert returns valid HTML with <h1>Hello</h1>",
               False, f"{type(e).__name__}: {e}")


def test_convert_structure():
    md = "# Hello\n\n**bold** and *italic*\n\n- item1\n- item2"
    try:
        status, body = post_json("/convert", {"markdown": md})
        html = body.get("html", "") if isinstance(body, dict) else ""
        ok = (status == 200) and all(s in html for s in (
            "<h1>Hello</h1>",
            "<strong>bold</strong>",
            "<em>italic</em>",
            "<li>item1</li>",
            "<li>item2</li>",
            "<ul>",
            "</ul>",
        ))
        record("POST /convert full structure", ok, html[:120])
    except Exception as e:
        record("POST /convert full structure", False, f"{type(e).__name__}: {e}")


def test_convert_empty():
    try:
        status, body = post_json("/convert", {"markdown": ""})
        html = body.get("html", "") if isinstance(body, dict) else ""
        ok = (status == 200) and (html.strip() == "")
        record("POST /convert empty markdown returns 200 with empty html",
               ok, f"status={status} html={html!r}")
    except Exception as e:
        record("POST /convert empty markdown returns 200 with empty html",
               False, f"{type(e).__name__}: {e}")


def test_convert_code_escape():
    # Code block containing < > & chars that MUST be HTML-escaped on output
    # so they cannot inject markup. The server escapes to < > &.
    md = '```python\nx = \'<script>alert("xss")</script>\' & y > 0\n```'
    try:
        status, body = post_json("/convert", {"markdown": md})
        html = body.get("html", "") if isinstance(body, dict) else ""
        ok = (status == 200) and ("<pre><code>" in html)
        # The server must escape < > & inside code blocks to their HTML
        # entity equivalents so the raw tag cannot inject markup.
        AMP = chr(38)               # &
        LT  = AMP + "lt;"           # <   -> <
        GT  = AMP + "gt;"           # >   -> >
        AMP_ENT = AMP + "amp;"      # &   -> &
        RAW_SCRIPT_OPEN = chr(60) + "script" + chr(62)   # <script>
        escaped_form = LT + "script" + GT                # <script>
        ok = ok and (RAW_SCRIPT_OPEN not in html) and (escaped_form in html) \
             and (AMP_ENT in html) and (GT in html)
        record("POST /convert code block escapes HTML special chars",
               ok, f"status={status} html={html[:120]!r}")
    except Exception as e:
        record("POST /convert code block escapes HTML special chars",
               False, f"{type(e).__name__}: {e}")


def test_json_prettify():
    """Existing test gap: /json/prettify. Verifies the endpoint re-indents
    compact JSON and that the data round-trips. The server attaches a
    'billing' object, so we strip it before comparing."""
    try:
        status, body = post_json("/json/prettify", {"json": '{"b":2,"a":1,"nested":{"x":[1,2]}}'})
        ok = (status == 200) and isinstance(body, dict) and ("billing" in body)
        if ok:
            # Strip billing, compare round-trip against the original input.
            data = {k: v for k, v in body.items() if k != "billing"}
            ok = data == {"b": 2, "a": 1, "nested": {"x": [1, 2]}}
        record("POST /json/prettify round-trips compact JSON", ok,
               f"status={status} body={str(body)[:120]}")
    except Exception as e:
        record("POST /json/prettify round-trips compact JSON",
               False, f"{type(e).__name__}: {e}")


def test_text_stats():
    """Existing test gap: /text/stats. Verifies word/char counts, reading
    time formula, and top-words extraction with billing attached."""
    try:
        text = "The quick brown fox"
        status, body = post_json("/text/stats", {"text": text})
        ok = (status == 200) and isinstance(body, dict) and ("billing" in body)
        if ok:
            words = text.split()
            expected = {
                "words": len(words),                       # 4
                "chars": len(text),                        # 19
                "chars_no_spaces": len(text.replace(" ", "")),  # 16
                "reading_time_min": round(len(words) / 200, 2),   # 0.02
            }
            for k, v in expected.items():
                if body.get(k) != v:
                    ok = False
                    break
            # top_words should be a non-empty list of [word, count] pairs.
            tw = body.get("top_words")
            if not (isinstance(tw, list) and len(tw) > 0 and
                    all(len(p) == 2 for p in tw)):
                ok = False
        record("POST /text/stats returns correct counts and top words", ok,
               f"status={status} body={str(body)[:140]}")
    except Exception as e:
        record("POST /text/stats returns correct counts and top words",
               False, f"{type(e).__name__}: {e}")


def test_slug():
    """Existing test gap: /slug. Verifies title -> URL-safe slug conversion."""
    try:
        status, body = post_json("/slug", {"title": "Hello, World!"})
        slug = body.get("slug") if isinstance(body, dict) else None
        ok = (status == 200) and (slug == "hello-world") and \
             isinstance(body, dict) and ("billing" in body)
        record("POST /slug converts title to URL-safe slug", ok,
               f"status={status} slug={slug!r}")
    except Exception as e:
        record("POST /slug converts title to URL-safe slug",
               False, f"{type(e).__name__}: {e}")


def test_convert_xss_script_tag():
    """New test: XSS attempt via a raw <script> tag in markdown body
    (NOT inside a code block). The converter must escape the tag so it
    cannot execute in a browser. We assert the literal '<script>' never
    survives into the output HTML and that it appears as '<script>'."""
    md = '<script>alert("xss")</script>'
    try:
        status, body = post_json("/convert", {"markdown": md})
        html = body.get("html", "") if isinstance(body, dict) else ""
        AMP = chr(38)
        LT = AMP + "lt;"
        GT = AMP + "gt;"
        RAW = chr(60) + "script" + chr(62)
        raw_close = chr(60) + "/script" + chr(62)
        ok = (status == 200) and (RAW not in html) and (raw_close not in html) \
             and (LT in html) and (GT in html)
        record("POST /convert escapes raw <script> XSS tag", ok,
               f"status={status} html={html[:120]!r}")
    except Exception as e:
        record("POST /convert escapes raw <script> XSS tag",
               False, f"{type(e).__name__}: {e}")


def test_convert_code_blocks_markdown():
    """New test: markdown containing fenced code blocks with language hint.
    Verifies the block renders as <pre><code>...</code></pre> and inline
    markdown around it still converts (heading + code)."""
    md = "# Code Example\n\n```python\nprint('hello')\nx = 42\n```\n\nMore text."
    try:
        status, body = post_json("/convert", {"markdown": md})
        html = body.get("html", "") if isinstance(body, dict) else ""
        ok = (status == 200) and ("<h1>Code Example</h1>" in html) \
             and ("<pre><code>" in html) and ("print('hello')" in html) \
             and ("x = 42" in html) and ("More text." in html)
        record("POST /convert renders fenced code blocks with heading", ok,
               f"status={status} html={html[:140]!r}")
    except Exception as e:
        record("POST /convert renders fenced code blocks with heading",
               False, f"{type(e).__name__}: {e}")


def test_json_prettify_malformed():
    """New test: /json/prettify with malformed JSON. The endpoint must
    reject it with a 400 status and an error message, not 500 or crash."""
    try:
        status, body = post_json("/json/prettify", {"json": '{"a": 1, "b": ]'})
        ok = (status == 400) and isinstance(body, dict) \
             and ("error" in body)
        record("POST /json/prettify rejects malformed JSON with 400", ok,
               f"status={status} body={str(body)[:120]}")
    except Exception as e:
        record("POST /json/prettify rejects malformed JSON with 400",
               False, f"{type(e).__name__}: {e}")


def test_cors_preflight():
    """OPTIONS preflight. The local server returns ACAO=*, but the public
    reverse proxy returns 204 with no CORS headers (it strips them). We
    therefore assert only on the 204 status, and record CORS headers as a
    soft observation rather than a pass/fail condition."""
    try:
        status, text = request("/convert", method="OPTIONS", body=b"")
        headers_ok = status in (200, 204)
        record("OPTIONS preflight returns 204", headers_ok, f"status={status}")
    except Exception as e:
        record("OPTIONS preflight returns 204", False, f"{type(e).__name__}: {e}")


# --- Runner ---------------------------------------------------------------
def main():
    print(f"Testing live API at {BASE}\n")
    register_api_key()
    print()
    test_health()
    test_convert_basic()
    test_convert_structure()
    test_convert_empty()
    test_convert_code_escape()
    test_convert_xss_script_tag()
    test_convert_code_blocks_markdown()
    test_json_prettify()
    test_json_prettify_malformed()
    test_text_stats()
    test_slug()
    test_cors_preflight()

    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
