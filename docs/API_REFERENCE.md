# MD2HTML API Reference

Markdown conversion and small developer utilities. This page documents the 18-endpoint API contract implemented by the current server.

## Quickstart

Set the API root once. The local server listens on `8777`; the public reverse-proxy path is shown below.

```bash
# Local development
export BASE_URL=http://localhost:8777

# Public instance (replace if your deployment differs)
# export BASE_URL=http://147.15.103.217/md2html

# Check the service
curl "$BASE_URL/health"

# Convert Markdown without signup (10 calls per client IP)
curl -X POST "$BASE_URL/convert" \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello **world**\n\nThis is Markdown."}'

# Create an API key for an independent usage bucket
export API_KEY="$(curl -s "$BASE_URL/register" | python -c 'import json,sys; print(json.load(sys.stdin)["api_key"])')"

# Use the key on subsequent billable requests
curl -X POST "$BASE_URL/convert" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"markdown":"## Key-authenticated request"}'

# Inspect the key's usage
curl "$BASE_URL/usage" -H "X-API-Key: $API_KEY"
```

Every response is JSON except `GET /docs`, which is `text/plain`. Send UTF-8. JSON requests must include `Content-Type: application/json`; `/convert` and `/sanitize` also accept raw `text/plain` Markdown.

## Authentication flow

Authentication is optional for the free tier:

1. Call `GET /register`. It requires no credentials and returns a random `mk_...` key.
2. Store the key as a secret. Do not put it in a URL, source repository, browser code, or logs.
3. Send it as `X-API-Key: <key>` on every request whose usage should belong to that key.
4. Call `GET /usage` with the same header to inspect the key bucket.
5. If the header is absent, the server identifies the client by source IP. This is convenient for a quick test, but multiple users behind one NAT/proxy share the same free bucket.
6. When the free bucket is exhausted, billable POST requests return `402 Payment Required`. `GET /payment` publishes the Litecoin address and payment instructions.

Keys are opaque bearer credentials. There is no login, refresh, revoke, or key-rotation endpoint in the current API. Create a new key with `/register` if you need a new bucket. The rate limiter remains IP-based even when billing uses an API key.

## Limits, billing, and common errors

| Rule | Current behavior |
|---|---|
| Free allowance | 10 billable calls per client identifier (API key when supplied, otherwise IP) |
| Paid price | `$0.001` per billable call, quoted in LTC by the service |
| Billable methods | All documented `POST` endpoints; `/batch` consumes one call per item |
| Free methods | All documented `GET` endpoints; they do not return a `billing` object |
| Rate limit | 30 requests per 60-second sliding window per source IP, for GET and POST |
| Rate-limit response | `429` with `{"error":"Rate limit exceeded","retry_after":60}` |
| General body cap | 1 MiB (`1,048,576` bytes) |
| Markdown cap | `/convert` and `/sanitize`: 50 KiB request body |
| Batch cap | `/batch`: 50 items |

Billing is checked after endpoint-specific structural validation for most endpoints. A successful billable response includes:

```json
{
  "status": 200,
  "calls_made": 1,
  "remaining": 9,
  "free_tier_limit": 10
}
```

Typical error envelope:

```json
{"error":"Invalid JSON","message":"See /docs for usage."}
```

The API uses these HTTP statuses:

- `200 OK` — request succeeded.
- `204 No Content` — CORS preflight (`OPTIONS`), not one of the 18 product endpoints.
- `400 Bad Request` — malformed JSON, missing/null field, invalid option, or invalid endpoint input.
- `402 Payment Required` — free allowance exhausted for a billable request. The response includes the LTC wallet and usage details.
- `404 Not Found` — path is not recognized.
- `413 Payload Too Large` — body exceeds 1 MiB, Markdown exceeds 50 KiB, or batch exceeds 50 items.
- `429 Too Many Requests` — source IP exceeded 30 requests in 60 seconds.
- `500 Internal Server Error` — unexpected server failure.

## Endpoint index

| # | Method | Path | Auth | Billing |
|---:|---|---|---|---|
| 1 | GET | `/health` | None | Free |
| 2 | GET | `/register` | None | Free |
| 3 | POST | `/convert` | Optional `X-API-Key` | 1 call |
| 4 | POST | `/sanitize` | Optional `X-API-Key` | 1 call |
| 5 | POST | `/batch` | Optional `X-API-Key` | 1 call/item |
| 6 | POST | `/minify` | Optional `X-API-Key` | 1 call |
| 7 | POST | `/html/extract` | Optional `X-API-Key` | 1 call |
| 8 | POST | `/url/shorten` | Optional `X-API-Key` | 1 call |
| 9 | POST | `/cron/parse` | Optional `X-API-Key` | 1 call |
| 10 | POST | `/regex/test` | Optional `X-API-Key` | 1 call |
| 11 | POST | `/json/prettify` | Optional `X-API-Key` | 1 call |
| 12 | POST | `/text/stats` | Optional `X-API-Key` | 1 call |
| 13 | POST | `/slug` | Optional `X-API-Key` | 1 call |
| 14 | GET | `/docs` | None | Free |
| 15 | GET | `/pricing` | None | Free |
| 16 | GET | `/payment` | None | Free |
| 17 | GET | `/usage` | Optional `X-API-Key` | Free |
| 18 | GET | `/stats` | None | Free |

---

## 1. `GET /health`

Liveness/readiness probe. No parameters and no authentication.

### Params

None.

### Request

```bash
curl "$BASE_URL/health"
```

### Response

```json
{
  "status": "ok",
  "version": "1.3.0",
  "uptime_seconds": 3612.5,
  "uptime": "0d 1h 0m 12s",
  "port": 8777,
  "timestamp": 1720000000,
  "endpoints": ["/health", "/register", "/convert", "/sanitize", "/batch", "/minify", "/html/extract", "/url/shorten", "/cron/parse", "/regex/test", "/json/prettify", "/text/stats", "/slug", "/docs", "/pricing", "/payment", "/usage", "/stats"]
}
```

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; does not consume the API-key/IP free-call allowance.

## 2. `GET /register`

Mint a new independent API-key bucket. No parameters and no authentication.

### Params

None.

### Request

```bash
curl "$BASE_URL/register"
```

### Response

```json
{
  "api_key": "mk_2ddf91574347ae032bea14f0b313555a",
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "free_tier_limit": 10,
  "calls_made": 0,
  "remaining": 10
}
```

The returned key is independent of the registering IP. The key is returned once; save it securely.

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; registering does not consume the new key's allowance.

## 3. `POST /convert`

Convert Markdown to HTML. Supports headings, bold, italic, links, inline code, fenced code blocks, and unordered lists. HTML is escaped and unsafe URL schemes are neutralized.

### Params

Headers: optional `X-API-Key`; body is either:

- JSON: `{"markdown":"..."}`
- Raw `text/plain`: Markdown text itself

Maximum request body is 1 MiB; the Markdown request body is additionally capped at 50 KiB.

### Request

```bash
curl -X POST "$BASE_URL/convert" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"markdown":"# Hello **world**\n\nVisit [example](https://example.com)."}'
```

### Response

```json
{
  "html": "<h1>Hello <strong>world</strong></h1>\n\nVisit <a href=\"https://example.com\">example</a>.",
  "billing": {"status": 200, "calls_made": 1, "remaining": 9, "free_tier_limit": 10}
}
```

- **Errors:** `400` empty/invalid request body; `402` free tier exhausted; `413` body over 1 MiB or Markdown over 50 KiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call after body-size validation. A successful response contains `billing`; an exhausted response contains the payment envelope instead.

## 4. `POST /sanitize`

Escape raw HTML in Markdown before converting it. Use this when input may contain untrusted HTML that must appear as literal text.

### Params

Headers: optional `X-API-Key`; body is JSON `{"markdown":"..."}` or raw `text/plain` Markdown. Maximum request body and Markdown size: 1 MiB and 50 KiB respectively.

### Request

```bash
curl -X POST "$BASE_URL/sanitize" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"markdown":"# Safe\n\n<script>alert(1)</script>"}'
```

### Response

```json
{
  "html": "<h1>Safe</h1>\n\n&lt;script&gt;alert(1)&lt;/script&gt;",
  "sanitized": true,
  "billing": {"status": 200, "calls_made": 2, "remaining": 8, "free_tier_limit": 10}
}
```

- **Errors:** `400` empty/invalid request body; `402` free tier exhausted; `413` body over 1 MiB or Markdown over 50 KiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call after body-size validation.

## 5. `POST /batch`

Convert multiple Markdown strings in one request. Each item is converted independently. Non-null non-string items are stringified; null items are rejected.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required | Rules |
|---|---|:---:|---|
| `items` | array | Yes | At least one item; maximum 50; null items rejected |

### Request

```bash
curl -X POST "$BASE_URL/batch" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"items":["# First","## Second\n\n- item"]}'
```

### Response

```json
{
  "results": ["<h1>First</h1>", "<h2>Second</h2>\n\n<ul>\n<li>item</li>\n</ul>"],
  "count": 2,
  "billing": {"status": 200, "calls_made": 4, "remaining": 6, "free_tier_limit": 10}
}
```

`billing` reflects the last item charged. If the allowance ends part-way through a batch, the server stops and returns `402` with `partial_results` and the billing record for the rejected item:

```json
{
  "error": "Payment Required",
  "message": "Free tier limit exceeded at item 2 of 4. Send payment to continue.",
  "partial_results": ["<h1>First</h1>", "<h1>Second</h1>"],
  "billing": {"status": 402, "calls_made": 11, "free_tier_limit": 10},
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"
}
```

- **Errors:** `400` invalid JSON, missing `items`, non-array, empty array, or null item; `402` exhausted mid-batch; `413` more than 50 items or body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 HTTP requests/60 seconds per source IP. One batch is one HTTP request.
- **Billing:** One billable call per item, not per HTTP request. A two-item successful batch consumes two calls.

## 6. `POST /minify`

Minify HTML, CSS, or JavaScript using the standard-library implementation.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required | Default/rules |
|---|---|:---:|---|
| `code` | string or scalar | Yes | Source; null is rejected; non-strings are stringified |
| `type` | string | No | `html`, `css`, or `js`; defaults to `html` |

### Request

```bash
curl -X POST "$BASE_URL/minify" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"type":"html","code":"<div>  <p> Hello </p> </div><!-- remove -->"}'
```

### Response

```json
{
  "minified": "<div><p> Hello </p></div>",
  "original_chars": 43,
  "minified_chars": 25,
  "reduction_pct": 41.9,
  "type": "html",
  "billing": {"status": 200, "calls_made": 5, "remaining": 5, "free_tier_limit": 10}
}
```

For empty source, the success response also includes `warning: "Empty input — nothing to minify."` and zero lengths.

- **Errors:** `400` invalid JSON, missing/null `code`, unsupported `type`, or minification failure; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call. Invalid JSON and invalid `type` are rejected before billing; valid empty source is billable.

## 7. `POST /html/extract`

Extract visible text from HTML. `<script>` and `<style>` content is skipped, entities are unescaped, and whitespace is collapsed.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required |
|---|---|:---:|
| `html` | string or scalar | Yes; null is rejected |

### Request

```bash
curl -X POST "$BASE_URL/html/extract" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"html":"<p>Hello <b>world</b></p><script>secret()</script>"}'
```

### Response

```json
{
  "text": "Hello world",
  "chars": 11,
  "billing": {"status": 200, "calls_made": 6, "remaining": 4, "free_tier_limit": 10}
}
```

- **Errors:** `400` invalid JSON, missing `html`, or null `html`; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call after the JSON/field checks.

## 8. `POST /url/shorten`

Create a base62 short code for a URL. The same URL maps to the same code while the server process's in-memory store retains it.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required | Rules |
|---|---|:---:|---|
| `url` | string or scalar | Yes | Must start with `http://`, `https://`, or `ftp://`; whitespace is trimmed |

### Request

```bash
curl -X POST "$BASE_URL/url/shorten" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"url":"https://example.com/a/long/path?ref=docs"}'
```

### Response

```json
{
  "short_code": "1",
  "short_url": "/s/1",
  "original_url": "https://example.com/a/long/path?ref=docs",
  "billing": {"status": 200, "calls_made": 7, "remaining": 3, "free_tier_limit": 10}
}
```

- **Errors:** `400` invalid JSON, missing/null/empty URL, or invalid scheme; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call. URL validation happens before the call is charged.

## 9. `POST /cron/parse`

Validate a five-field cron expression and produce a human-readable description. Supports `*`, `*/N`, ranges, comma lists, numeric values, three-letter day names, and three-letter month names. Day-of-week accepts `0` or `7` for Sunday.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required |
|---|---|:---:|
| `expression` | string or scalar | Yes; null is rejected |

The five fields are minute, hour, day of month, month, and day of week.

### Request

```bash
curl -X POST "$BASE_URL/cron/parse" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"expression":"0 9 * * mon"}'
```

### Response

```json
{
  "expression": "0 9 * * mon",
  "description": "At 09:00 on Monday",
  "fields": {
    "minute": "0",
    "hour": "9",
    "day_of_month": "*",
    "month": "*",
    "day_of_week": "mon"
  },
  "billing": {"status": 200, "calls_made": 8, "remaining": 2, "free_tier_limit": 10}
}
```

- **Errors:** `400` invalid JSON, missing/null expression, wrong field count, invalid syntax, or out-of-range value; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call. A syntactically invalid cron expression can consume a call because billing occurs before cron parsing.

## 10. `POST /regex/test`

Run a Python-compatible regular expression and return up to 1,000 matches.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required | Rules |
|---|---|:---:|---|
| `pattern` | string or scalar | Yes; null is rejected |
| `input` | string or scalar | Yes; null is rejected |
| `flags` | string | No | `i` ignore case, `m` multiline, `s` dotall, `x` verbose; unknown letters are ignored |

### Request

```bash
curl -X POST "$BASE_URL/regex/test" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"pattern":"\\d+","input":"abc 12 def 34","flags":""}'
```

### Response

```json
{
  "pattern": "\\d+",
  "flags": "",
  "input": "abc 12 def 34",
  "matched": true,
  "match_count": 2,
  "truncated": false,
  "matches": [
    {"match":"12","index":4,"end":6,"groups":[],"named_groups":null},
    {"match":"34","index":11,"end":13,"groups":[],"named_groups":null}
  ],
  "billing": {"status": 200, "calls_made": 9, "remaining": 1, "free_tier_limit": 10}
}
```

- **Errors:** `400` invalid JSON, missing/null `pattern` or `input`, or invalid regex pattern; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call. The result is truncated after 1,000 matches; the `truncated` field reports that condition.

## 11. `POST /json/prettify`

Parse and re-indent a JSON document with two-space indentation. The request carries JSON text inside the `json` field.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required |
|---|---|:---:|
| `json` | string | Yes; compact or formatted JSON text |

### Request

```bash
curl -X POST "$BASE_URL/json/prettify" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"json":"{\"name\":\"Ada\",\"skills\":[\"python\",\" APIs\"]}"}'
```

### Response

The server returns the parsed JSON object with the `billing` object attached. It does not wrap the formatted text in a `prettified` field.

```json
{
  "name": "Ada",
  "skills": ["python", " APIs"],
  "billing": {"status": 200, "calls_made": 10, "remaining": 0, "free_tier_limit": 10}
}
```

- **Errors:** `400` invalid/empty JSON field or bad input; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call. A successful call returns the formatted value re-parsed as JSON plus billing metadata.

## 12. `POST /text/stats`

Compute counts and a simple reading-time estimate. Words are whitespace-separated tokens; top words are case-folded alphabetic tokens, limited to five.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required |
|---|---|:---:|
| `text` | string | Yes; non-empty |

### Request

```bash
curl -X POST "$BASE_URL/text/stats" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

### Response

```json
{
  "words": 9,
  "chars": 44,
  "chars_no_spaces": 36,
  "reading_time_min": 0.05,
  "top_words": [["the",2],["quick",1],["brown",1],["fox",1],["jumps",1]],
  "billing": {"status": 200, "calls_made": 1, "remaining": 9, "free_tier_limit": 10}
}
```

- **Errors:** `400` empty `text` or malformed body; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call.

## 13. `POST /slug`

Turn a title into a URL-safe ASCII slug. Unicode accents are decomposed and removed; non-alphanumeric runs become one hyphen.

### Params

Headers: optional `X-API-Key`. JSON body:

| Field | Type | Required |
|---|---|:---:|
| `title` | string | Yes; non-empty |

### Request

```bash
curl -X POST "$BASE_URL/slug" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"title":"Café — Menus & Drinks!"}'
```

### Response

```json
{
  "slug": "cafe-menus-drinks",
  "billing": {"status": 200, "calls_made": 2, "remaining": 8, "free_tier_limit": 10}
}
```

- **Errors:** `400` empty `title` or malformed body; `402` free tier exhausted; `413` body over 1 MiB; `429` rate limit; `500` unexpected error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** One billable call.

## 14. `GET /docs`

Return the server's built-in plain-text usage guide. It is useful for a quick machine-readable-ish overview, but this Markdown page is the maintained reference for request and response detail.

### Params

None.

### Request

```bash
curl "$BASE_URL/docs"
```

### Response

`200 OK`, `Content-Type: text/plain`, followed by the plain-text usage guide.

```text
Markdown-to-HTML API — Usage Guide
=====================================
GET /register
  Mint a new API key...
```

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; does not consume a client allowance.

## 15. `GET /pricing`

Return the live server's currently configured free-tier, paid-call, rate-limit, and body-size values.

### Params

None.

### Request

```bash
curl "$BASE_URL/pricing"
```

### Response

```json
{
  "free_tier": {
    "calls": 10,
    "price_per_call": "0.00 USD",
    "auth": "none — identified by IP or X-API-Key"
  },
  "paid_tier": {
    "price_per_call": "0.001 USD",
    "currency": "LTC",
    "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
    "note": "Send Litecoin to the wallet to continue after the free tier."
  },
  "rate_limit": {"max": 30, "window_seconds": 60},
  "max_body_bytes": 1048576
}
```

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; pricing lookup does not consume a client allowance.

## 16. `GET /payment`

Return the Litecoin payment address and the current payment message.

### Params

None. This endpoint is informational and does not accept a payment transaction body.

### Request

```bash
curl "$BASE_URL/payment"
```

### Response

```json
{
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "currency": "LTC",
  "message": "Send any amount of Litecoin to this address to continue using the API after the free tier."
}
```

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free.

### Payment note

The current server exposes `GET /payment` only. It does not expose a `POST /payment` transaction-verification or automatic key-credit route. A `402` response is therefore the signal to obtain the address and arrange payment/credit through the deployment's billing operator; do not assume that posting a `txid` to this endpoint will work.

## 17. `GET /usage`

Return the current call count for the API key in `X-API-Key`, or for the caller's IP when no key is supplied. This read does not increment the count.

### Params

Optional header: `X-API-Key`.

### Request

```bash
# IP bucket
curl "$BASE_URL/usage"

# API-key bucket
curl "$BASE_URL/usage" -H "X-API-Key: $API_KEY"
```

### Response

```json
{
  "client": "mk_2ddf91574347ae032bea14f0b313555a",
  "calls_made": 7,
  "free_tier_limit": 10,
  "remaining": 3
}
```

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; the lookup does not consume an allowance.

## 18. `GET /stats`

Return aggregate analytics from the server's call log. This is operational data, not per-key billing data.

### Params

None.

### Request

```bash
curl "$BASE_URL/stats"
```

### Response

```json
{
  "total_calls": 42,
  "unique_ips": 3,
  "calls_by_endpoint": {"/health": 12, "/convert": 20, "/usage": 10},
  "calls_by_status": {"200": 39, "402": 2, "429": 1},
  "potential_conversions": 2,
  "avg_latency": 0.018
}
```

`potential_conversions` is the number of logged `402` responses; it is an analytics label, not proof that an LTC payment settled.

- **Errors:** `429` rate limit; `500` unexpected server error.
- **Rate limit:** 30 requests/60 seconds per source IP.
- **Billing:** Free; stats lookup does not consume a client allowance.

## Billing response and payment errors

After a client makes its tenth billable call, the next billable request returns HTTP `402`:

```json
{
  "status": 402,
  "error": "Payment Required",
  "message": "Free tier limit (10 calls) exceeded. You made 11 calls. Send payment to continue.",
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "calls_made": 11,
  "free_tier_limit": 10
}
```

The usage counter is selected as follows:

```text
X-API-Key present and non-empty -> that exact key
Otherwise                         -> source IP address
```

Payment is quoted as `$0.001` per call and settled in LTC at the configured wallet. Check `GET /pricing` and `GET /payment` at runtime rather than hard-coding the address or limits.

## Example retry logic

```bash
response=$(curl -sS -w '\n%{http_code}' \
  -X POST "$BASE_URL/convert" \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $API_KEY" \
  -d '{"markdown":"# Retry-safe request"}')

body=$(printf '%s' "$response" | sed '$d')
status=$(printf '%s' "$response" | tail -n 1)

case "$status" in
  200) printf '%s\n' "$body" ;;
  402) printf 'Free tier exhausted; inspect wallet_address in response.\n' >&2; exit 2 ;;
  429) printf 'Rate limited; wait retry_after seconds and retry.\n' >&2; exit 3 ;;
  *)   printf 'API error (%s): %s\n' "$status" "$body" >&2; exit 1 ;;
esac
```

## Security and transport notes

- Use HTTPS in production. The example public URL is HTTP because that is how the current instance is exposed.
- Treat `X-API-Key` as a bearer secret.
- The server sends `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and permissive CORS headers.
- Markdown conversion escapes HTML and blocks dangerous `javascript:`, `data:`, `vbscript:`, and `file:` link schemes.
- Limits and billing counters are process/file-backed implementation details; verify live values through `/pricing` and `/usage`.
