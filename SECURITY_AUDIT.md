# Security Audit — server.py + billing.py (MD2HTML API)

Reviewed: `server.py` (~1297 lines, stdlib `http.server`, v1.2.0, port 8777 behind nginx on Oracle VPS) and `billing.py` (~170 lines). LTC wallet receives payments. Note: `server.py` currently contains unresolved git merge-conflict markers (`<<<<<<<` / `=======` / `>>>>>>>`); review is against the newer v1.2.0 "stashed" side (lines 422–1296), which is the effective code.

## Findings

### 1. FAIL — Billing bypass via X-API-Key spoofing
`billing.py` `record_call(api_key)` (line 78) looks up whatever string is passed in `usage.json` and creates a fresh zero-count entry if the key is not found (line 86–87). `server.py` `billing_client_id` (line 464) trusts the raw `X-API-Key` header verbatim — no validation it was ever minted by `/register`. So an attacker cycling arbitrary header values (`X-API-Key: a`, `b`, `c`, …) gets a brand-new 10-call free bucket each time, bypassing billing infinitely. The `mk_` prefix is "[p]urely cosmetic; not enforced anywhere" (billing.py line 24–25). **Fix:** verify the key exists in `usage.json` with `kind == "api_key"` before honoring it; reject unknown keys (treat as IP or 403).

### 2. PASS — No directory traversal in /docs or /convert
Neither endpoint touches the filesystem with user-controlled paths. `/docs` (line 943) returns the hard-coded `GUIDE` string. `/convert` (line 1051) reads the POST body and runs `md_to_html` — pure string transforms. The only `open()` is `index.html` on `/` (line 1001) via `os.path.join(__file__ dir, "index.html")` — the filename is a literal, not user input. No `..` reaches any path.

### 3. PASS (with caveat) — XSS largely mitigated, one residual gap
Raw `< > &` are HTML-escaped before emission (line 534). Code-block contents are escaped on extraction before reinsertion (lines 522–527). Link URLs pass through `safe_url` (line 474), which rewrites `javascript:`, `data:`, `vbscript:`, `file:` schemes to `#`. **Caveat:** `safe_url` blocks the four schemes but does NOT allowlist only `http(s):`, `mailto:`, or relative URLs — exotic schemes (e.g. `blob:`, custom protocol handlers) survive into the `href` attribute. This is a partial fail. Recommend switching to an allowlist (reject anything not `http(s)://`, `mailto:`, or `/`-relative). The `/sanitize` endpoint additionally pre-escapes raw HTML, which is good.

### 4. PASS — API key generation is cryptographically secure
`billing.py` `generate_api_key` (line 45) uses `secrets.token_hex(16)` — 128 bits of CSPRNG entropy, prefixed with `mk_`. `secrets` is the correct module (uses `os.urandom`). The keys are unpredictable and not brute-forceable. `/register` (server.py line 971) calls `register_client(ip)` which mints, persists, and returns the key. No weakness in generation. (**Note:** security of *use* is broken — see Finding 1; the keys are well-made but unenforced.)

### 5. PASS — 1MB body limit is sufficient and enforced
`MAX_BODY = 1024 * 1024` (line 431). `_read_body` (line 1022) reads `Content-Length`, rejects >1MB with a 413 *before* reading (line 1033). `/convert` and `/sanitize` additionally cap markdown input at 50KB (lines 1058, 1102), and `/batch` caps at 50 items (line 1183). The rebind is read after the cap check, so a `Content-Length: 999999999` attack is rejected without allocation. 1MB is ample for markdown/JSON text payloads.

## Summary

| # | Check | Result |
|---|-------|--------|
| 1 | Billing bypass via X-API-Key spoof | **FAIL** |
| 2 | Directory traversal in /docs, /convert | **PASS** |
| 3 | XSS in HTML output | **PASS** (caveat: broaden scheme blocklist → allowlist) |
| 4 | Secure API key generation | **PASS** |
| 5 | 1MB body limit sufficient | **PASS** |

**Top priority:** Fix Finding 1 — unauthenticated header minting is an infinite billing bypass. Secondary: harden `safe_url` to an allowlist. Also resolve the unresolved git merge conflict in `server.py` before deploy.

---
*Fresh review of v1.2.0 code. Re-test after each fix.*
