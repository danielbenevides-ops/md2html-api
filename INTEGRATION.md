# Integration Guide — md2html LTC API

**Base URL:** `http://147.15.103.217/md2html/`
**Currency:** Litecoin (LTC)
**Wallet:** `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`
**Free tier:** 10 calls per IP, then HTTP `402 Payment Required`.

---

## Quick Start

Get an API key, make your first conversion, and track usage in three steps.

**1. Register** — get a free API key:

```bash
curl -X POST http://147.15.103.217/md2html/register
```

**2. Convert** — markdown → HTML (replace `YOUR_KEY`):

```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H 'X-API-Key: YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"markdown": "# Hello"}'
```

**3. Check usage** — see remaining calls:

```bash
curl http://147.15.103.217/md2html/usage -H 'X-API-Key: YOUR_KEY'
```

### Python (requests)

```python
import requests
BASE = "http://147.15.103.217/md2html"
key = "YOUR_KEY"
hdr = {"X-API-Key": key}

# Register first (one-time) to get a key:
#  resp = requests.post(f"{BASE}/register").json(); key = resp["api_key"]

r = requests.post(f"{BASE}/convert", headers=hdr,
                  json={"markdown": "# Hello"})
print(r.json())

r = requests.get(f"{BASE}/usage", headers=hdr)
print(r.json())
```

### JavaScript (fetch)

```javascript
const BASE = "http://147.15.103.217/md2html";
const key = "YOUR_KEY";
const hdr = { "X-API-Key": key };

// Register once: const k = await (await fetch(`${BASE}/register`, {method:"POST"})).json();

const res = await fetch(`${BASE}/convert`, {
  method: "POST",
  headers: { ...hdr, "Content-Type": "application/json" },
  body: JSON.stringify({ markdown: "# Hello" }),
});
console.log(await res.json());

const usage = await (await fetch(`${BASE}/usage`, { headers: hdr })).json();
console.log(usage);
```

> 💡 Replace `YOUR_KEY` with the key returned by `/register`. No key? Calls fall
> back to IP-based billing (10 free per IP, then `402 Payment Required`).

---

## Quick Start — Copy-Paste Code (IP-keyed / no API key)

### Python (requests)

```python
import requests

BASE = "http://147.15.103.217/md2html"

# --- Convert markdown to HTML ---
r = requests.post(f"{BASE}/convert", json={"markdown": "# Hello **world**"})
print(r.status_code, r.json())
# 200 {'html': '<h1>Hello <strong>world</strong></h1>\n', 'chars': 19, ...}

# --- Check usage ---
r = requests.get(f"{BASE}/usage")
print(r.json())
# {'client': '1.2.3.4', 'calls_made': 3, 'free_tier_limit': 10, 'remaining': 7}

# --- Get payment address (when you hit 402) ---
r = requests.get(f"{BASE}/payment")
print(r.json())
# {'wallet_address': 'Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM', 'currency': 'LTC', ...}

# --- Robust call with 402 handling ---
def call(endpoint, **kwargs):
    r = requests.post(f"{BASE}/{endpoint}", json=kwargs, timeout=10)
    if r.status_code == 402:
        pay = requests.get(f"{BASE}/payment").json()
        raise PermissionError(f"Free tier exhausted. Send LTC to {pay['wallet_address']}")
    r.raise_for_status()
    return r.json()

html = call("convert", markdown="## Heading\n\nSome **bold** text.")
```

### JavaScript (fetch)

```javascript
const BASE = "http://147.15.103.217/md2html";

// --- Convert markdown to HTML ---
const res = await fetch(`${BASE}/convert`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ markdown: "# Hello **world**" }),
});
const data = await res.json();
console.log(res.status, data);
// 200 { html: '<h1>Hello <strong>world</strong></h1>\n', chars: 19, ... }

// --- Check usage ---
const usage = await (await fetch(`${BASE}/usage`)).json();
console.log(usage);
// { client: '1.2.3.4', calls_made: 3, free_tier_limit: 10, remaining: 7 }

// --- Get payment address ---
const pay = await (await fetch(`${BASE}/payment`)).json();
console.log(pay);
// { wallet_address: 'Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM', currency: 'LTC', ... }

// --- Robust call with 402 handling ---
async function call(endpoint, payload) {
  const res = await fetch(`${BASE}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.status === 402) {
    const pay = await (await fetch(`${BASE}/payment`)).json();
    throw new Error(`Free tier exhausted. Send LTC to ${pay.wallet_address}`);
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

const result = await call("convert", { markdown: "## Heading\n\n**bold**" });
```

### curl

```bash
# Convert markdown to HTML
curl -X POST http://147.15.103.217/md2html/convert \
     -H "Content-Type: application/json" \
     -d '{"markdown":"# Hello **world**"}'

# Prettify JSON
curl -X POST http://147.15.103.217/md2html/json/prettify \
     -H "Content-Type: application/json" \
     -d '{"json":"{\"b\":2,\"a\":1}"}'

# Text statistics
curl -X POST http://147.15.103.217/md2html/text/stats \
     -H "Content-Type: application/json" \
     -d '{"text":"The quick brown fox jumps over the lazy dog."}'

# Generate slug
curl -X POST http://147.15.103.217/md2html/slug \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World! My First Post"}'

# Check API health
curl http://147.15.103.217/md2html/health

# View API docs
curl http://147.15.103.217/md2html/docs

# Get payment info (wallet address)
curl http://147.15.103.217/md2html/payment

# Check your usage
curl http://147.15.103.217/md2html/usage

# Get server statistics
curl http://147.15.103.217/md2html/stats
```

---

## All 9 Endpoints — Reference & Examples

### 1. `GET /health` — Health Check

Returns server status. Not billed.

**curl:**
```bash
curl http://147.15.103.217/md2html/health
```
**Response:**
```json
{"status": "ok", "service": "md2html"}
```

---

### 2. `POST /convert` — Markdown → HTML

Converts Markdown text to styled HTML. Billed per call.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `markdown` | string | Yes | Markdown source text |

**curl:**
```bash
curl -X POST http://147.15.103.217/md2html/convert \
     -H "Content-Type: application/json" \
     -d '{"markdown":"# Title\n\nSome **bold** and *italic* text."}'
```
**Python:**
```python
r = requests.post(f"{BASE}/convert", json={"markdown": "# Title\n\n**bold** and *italic*"})
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/convert`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({markdown: "# Title\n\n**bold** and *italic*"})
});
console.log(await r.json());
```
**Response:**
```json
{
  "html": "<h1>Title</h1>\n<p>Some <strong>bold</strong> and <em>italic</em> text.</p>\n",
  "chars": 38
}
```

---

### 3. `POST /json/prettify` — Prettify JSON

Pretty-prints / reformats a JSON string with sorted keys.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `json` | string | Yes | Raw JSON string to prettify |

**curl:**
```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
     -H "Content-Type: application/json" \
     -d '{"json":"{\"b\":2,\"a\":1}"}'
```
**Python:**
```python
r = requests.post(f"{BASE}/json/prettify", json={"json": '{"b":2,"a":1}'})
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/json/prettify`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({json: '{"b":2,"a":1}'})
});
console.log(await r.json());
```
**Response:**
```json
{"pretty": "{\n  \"a\": 1,\n  \"b\": 2\n}"}
```

---

### 4. `POST /text/stats` — Text Statistics

Returns word count, character count, sentence count, and reading-time estimate.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Input text to analyze |

**curl:**
```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
     -H "Content-Type: application/json" \
     -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```
**Python:**
```python
r = requests.post(f"{BASE}/text/stats", json={"text": "The quick brown fox jumps."})
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/text/stats`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({text: "The quick brown fox jumps."})
});
console.log(await r.json());
```
**Response:**
```json
{
  "words": 6,
  "chars": 31,
  "sentences": 1,
  "reading_time_min": 0.03
}
```

---

### 5. `POST /slug` — Generate URL Slug

Converts text to a URL-safe slug.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Text to slugify |

**curl:**
```bash
curl -X POST http://147.15.103.217/md2html/slug \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello World! My First Post"}'
```
**Python:**
```python
r = requests.post(f"{BASE}/slug", json={"text": "Hello World! My First Post"})
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/slug`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({text: "Hello World! My First Post"})
});
console.log(await r.json());
```
**Response:**
```json
{"slug": "hello-world-my-first-post"}
```

---

### 6. `GET /docs` — API Documentation

Returns this documentation as JSON/HTML. Not billed.

**curl:**
```bash
curl http://147.15.103.217/md2html/docs
```
**Python:**
```python
r = requests.get(f"{BASE}/docs")
print(r.text)
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/docs`);
console.log(await r.text());
```

---

### 7. `GET /payment` — Payment Info

Returns the LTC wallet address and payment instructions. Not billed.

**curl:**
```bash
curl http://147.15.103.217/md2html/payment
```
**Python:**
```python
r = requests.get(f"{BASE}/payment")
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/payment");
console.log(await r.json());
```
**Response:**
```json
{
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "currency": "LTC",
  "message": "Send any amount of Litecoin to this address to continue usage."
}
```

---

### 8. `GET /usage` — Your Usage

Returns your IP's call count and remaining free calls. Not billed.

**curl:**
```bash
curl http://147.15.103.217/md2html/usage
```
**Python:**
```python
r = requests.get(f"{BASE}/usage")
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/usage");
console.log(await r.json());
```
**Response:**
```json
{
  "client": "203.0.113.42",
  "calls_made": 7,
  "free_tier_limit": 10,
  "remaining": 3
}
```

---

### 9. `GET /stats` — Server Statistics

Returns aggregate server statistics (total calls, unique clients, uptime). Not billed.

**curl:**
```bash
curl http://147.15.103.217/md2html/stats
```
**Python:**
```python
r = requests.get(f"{BASE}/stats")
print(r.json())
```
**JavaScript:**
```javascript
const r = await fetch(`${BASE}/stats");
console.log(await r.json());
```
**Response:**
```json
{
  "total_calls": 1542,
  "unique_clients": 37,
  "uptime_hours": 128.5
}
```

---

## Pricing

| Tier | Cost | Allowance |
|------|------|-----------|
| **Free** | $0 | 10 API calls per IP address (billed endpoints only) |
| **Paid** | Any LTC amount | Counter reset by operator after manual payment verification |

### Billed vs. Not-Billed Endpoints

| Billed (counts toward 10 free) | Free (unlimited) |
|---|---|
| `/convert` | `/health` |
| `/json/prettify` | `/docs` |
| `/text/stats` | `/payment` |
| `/slug` | `/usage` |
| | `/stats` |

### How to Pay After Free Tier

1. **Check usage** → `GET /usage` to see remaining calls.
2. **Get wallet** → `GET /payment` returns the LTC address:
   `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`
3. **Send LTC** from any wallet (any amount — honor system). Save your **txid**.
4. **Send txid to operator** (out-of-band: email/DM). Operator verifies on
   `https://chain.so/address/Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`, then runs
   `reset_usage(<your IP>)` to clear your counter.
5. **Call again.** Counter resets; you get another free-tier block.

> ⚠️ **No automatic verification yet.** Payment is honor-system — the server
> does not watch the LTC chain. Future: BlockCypher webhook + `/unlock`
> endpoint with txid verification.

### Rate Limit / 402 Handling

After 10 billed calls, the server returns `HTTP 402 Payment Required` with:
```json
{
  "status": 402,
  "error": "Free tier limit reached",
  "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
  "currency": "LTC"
}
```
Handle gracefully in code:
```python
if r.status_code == 402:
    pay = requests.get(f"{BASE}/payment").json()
    print(f"Send LTC to {pay['wallet_address']}")
```

---

## Server Internals (Operator Notes)

### Wallet address source
`server.py` reads `wallet.json` (same dir), falls back to hardcoded constant:
```python
WALLET_ADDRESS = json.load(open(_WALLET_FILE)).get("address",
    "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"
```
Override via env: `PAYMENT_WALLET`.

### Billing check (every billable path)
```python
bill = record_call(client_ip)
if bill.get("status") == 402:
    self.send(402, json.dumps(bill))  # Payment Required + wallet
    return
```

### Manual reset (operator action)
```bash
# In Python console:
import billing; billing.reset_usage("<client IP>")
# Or restart server (wipes usage.json)
```

### Local verification
```bash
python server.py &
curl localhost:8777/convert -d '## x' > /dev/null   # repeat 12x
curl localhost:8777/usage                              # remaining: 0
curl localhost:8777/convert -d '## x'                  # 402 + wallet
```

## Changelog
- Server uses **LTC** (Litecoin). Wallet: `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`.
- 9 endpoints live: `/health`, `/convert`, `/json/prettify`, `/text/stats`,
  `/slug`, `/docs`, `/payment`, `/usage`, `/stats`.
- Free tier: **10 calls/IP** on billed endpoints; then `402`.
- `/register` (API keys): **not yet implemented**. Billing is IP-keyed.
- `/unlock` (txid verification): **not yet implemented**. Manual reset only.
- Automatic LTC chain verification: **planned** via BlockCypher webhook.
