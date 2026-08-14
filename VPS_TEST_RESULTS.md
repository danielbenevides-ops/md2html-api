# MD2HTML API — External Endpoint Test Results

**Base URL:** `http://147.15.103.217/md2html/`  
**Tested:** Friday, August 07, 2026  
**Method:** curl from external host  

## Summary

| # | Endpoint | HTTP Status | Result |
|---|----------|:-----------:|--------|
| 1 | `GET /health` | 200 | ✅ PASS |
| 2 | `POST /convert` | 200 | ✅ PASS |
| 3 | `GET /payment` | 200 | ✅ PASS |
| 4 | `GET /usage` | 200 | ✅ PASS |
| 5 | `GET /stats` | 200 | ✅ PASS |
| 6 | `GET /docs` | 200 | ✅ PASS |
| 7 | `GET /` (landing) | 200 | ✅ PASS |

**All 7 endpoints PASSED.** 0 failures.

---

## Detailed Results

### 1. GET /health — ✅ PASS (200)

**Status:** `200`  
**Body:**
```json
{
  "status": "ok",
  "version": "1.1.0",
  "uptime_seconds": 533.5,
  "uptime": "0d 0h 8m 53s",
  "port": 8777,
  "timestamp": 1786107873,
  "endpoints": ["/health", "/convert", "/docs", "/payment", "/usage", "/stats"]
}
```

---

### 2. POST /convert — ✅ PASS (200)

**Request:** `{"markdown": "# Hello"}`  
**Status:** `200`  
**Body:**
```json
{
  "html": "<h1>Hello</h1>",
  "billing": {
    "status": 200,
    "calls_made": 5,
    "remaining": 5,
    "free_tier_limit": 10
  }
}
```

**Note:** Markdown→HTML conversion working correctly. Billing info included (free tier: 10 calls/IP).

---

### 3. GET /payment — ✅ PASS (200)

**Status:** `200`  
**Body:**
```json
{
  "wallet_address": "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG",
  "currency": "LTC",
  "message": "Send any amount of Litecoin to this address to continue using the API after the free tier."
}
```

---

### 4. GET /usage — ✅ PASS (200)

**Status:** `200`  
**Body:**
```json
{
  "client": "127.0.0.1",
  "calls_made": 5,
  "free_tier_limit": 10,
  "remaining": 5
}
```

---

### 5. GET /stats — ✅ PASS (200)

**Status:** `200`  
**Body:**
```json
{
  "total_calls": 21,
  "unique_ips": 1,
  "calls_by_endpoint": {
    "/health": 11,
    "/convert": 5,
    "/payment": 2,
    "/health`": 1,
    "/health%60": 1,
    "/usage": 1
  },
  "avg_latency": 0.0
}
```

---

### 6. GET /docs — ✅ PASS (200)

**Status:** `200`  
**Body (plain text guide, snippet):**
```
Markdown-to-HTML API — Usage Guide
=====================================
POST /convert
  Body: raw markdown text (Content-Type: text/plain or application/json {"markdown": "..."})
  Returns: {"html": "<converted html string>", "billing": {...}}
  Supported: headings, bold, italic, links, inline/block code, unordered lists.
  Free tier: 10 calls per IP. Then 402 + LTC wallet address.

GET /health   -> {"status":"ok","version":"...","uptime_seconds":N,"port":8777,...}
GET /docs     -> this guide
GET /payment  -> {"wallet_address": "...", "currency": "LTC"}
GET /usage    -> {"calls_made": N, "remaining": N}
GET /stats    -> {"total_calls": N, "unique_ips": N, ...}

Rate limit: 30 requests/minute per IP. Max body: 1MB.
```

---

### 7. GET / (landing page) — ✅ PASS (200)

**Status:** `200`  
**Body:** Full HTML landing page (5,267 bytes), dark-themed, titled "MD2HTML API — Convert Markdown to HTML via API". Contains usage examples, pricing section, email signup form. Footer: "MD2HTML API — autonomous business, served on port 8777. © 2026".

**Snippet:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MD2HTML API — Convert Markdown to HTML via API</title>
...
<footer>
  MD2HTML API — autonomous business, served on port 8777.
  <span class="accent">&copy; 2026</span>
</footer>
```

---

## Test Verdict

✅ **All 7 endpoints operational externally.** The MD2HTML API at `http://147.15.103.217/md2html/` is fully live and responding correctly from an external host. Markdown→HTML conversion works, billing/usage tracking functions, and the landing page renders.
