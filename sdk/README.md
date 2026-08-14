# md2html-api

A tiny, zero-dependency **Node.js SDK** for the [MD2HTML API](https://147.15.103.217.sslip.io/md2html/) — a Markdown-to-HTML micropayment service that bills per call in Litecoin.

- ✨ **Zero dependencies** — uses the global `fetch` built into Node.js 18+
- 🧩 Conversion, utility, usage, payment, and claim methods in one `MD2HTMLClient`
- 💰 Billing: 10 free calls, then **0.001 LTC / 100 prepaid calls**
- 🔑 Optional API key + `X-API-Key` header (falls back to IP-based billing)
- ⏱️ Built-in request timeout via `AbortController`
- 📦 CommonJS + ESM dual export

## Install

### From the repo

```bash
cd autonomous-business-product/sdk
npm install           # validates the package (no deps to download)
```

### Local package symlink (use as a library elsewhere)

```bash
# Inside the sdk/ directory:
npm link

# In your project:
npm link md2html-api
```

### From npm (once published)

```bash
npm install md2html-api
```

## Quick start

```js
// CommonJS
const { MD2HTMLClient } = require('md2html-api');

// ESM
// import { MD2HTMLClient } from 'md2html-api';

const client = new MD2HTMLClient({
  apiKey: 'mk_your_api_key',   // optional; omit for IP-based billing
  // baseUrl: 'https://147.15.103.217.sslip.io/md2html',  // optional override
  // timeoutMs: 30000,                          // optional (default 30s)
});

// Convert Markdown → HTML
const { html, billing } = await client.convert('# Hello **world** & *go*');
console.log(html);

// Mint a fresh API key + LTC wallet in one call
const key = await client.register();
client.apiKey = key.api_key;
console.log(key.wallet_address, key.remaining);

// After sending a package and waiting for one confirmation:
// const claim = await client.claimPayment('<64-hex-litecoin-txid>');
```

## API reference

All methods are **async** and return the parsed JSON response body. On a non-2xx
status they reject with an `Error` exposing `.status`, `.url`, and `.body`.

| Method             | Endpoint           | Description                                             |
| ------------------ | ------------------ | ------------------------------------------------------- |
| `convert(md)`      | `POST /convert`    | Convert a Markdown string to HTML.                      |
| `jsonPrettify(json)`| `POST /json/prettify` | Pretty-print a compact JSON string (2-space indent). |
| `textStats(text)`  | `POST /text/stats` | Word/char counts, reading time, top words.              |
| `slug(title)`      | `POST /slug`       | Generate a URL-safe slug from a title.                  |
| `register()`       | `GET /register`    | Mint a new API key + LTC wallet address.                |
| `health()`         | `GET /health`       | Liveness probe (uptime, version). No auth.             |
| `docs()`           | `GET /docs`         | Interactive API documentation.                        |
| `payment()`        | `GET /payment`      | LTC wallet address for topping up quota.               |
| `claimPayment(txid)` | `POST /payment/claim` | Verify a confirmed txid and add prepaid calls.       |
| `usage(opts?)`     | `GET /usage`        | Quota used / remaining (by API key or IP).             |
| `stats()`           | `GET /stats`        | Public aggregate service metrics.                      |

### Per-call API key override

Every method accepts `{ apiKey }` to override the constructor key for a single
request, sent as the `X-API-Key` header:

```js
await client.usage({ apiKey: 'mk_other_key' });
await client.convert('# x', { apiKey: 'mk_other_key' });
```

## Billing & rate limits

- **Free tier**: 10 free calls per client (IP or API key) across all POST endpoints.
- **Prepaid calls**: 0.001 LTC credits 100 calls. After one confirmation, call
  `claimPayment(txid)` using a managed API key. A txid is globally single-use.
- **Rate limit**: 30 requests / minute / IP.
- **Max body**: 1 MB (`/convert` caps Markdown input at 50 KB).

## Requirements

- **Node.js 18+** (global `fetch`). Test with `node -v`.
- No build step. No transitive dependencies.

## Test

Run the bundled smoke test against the live API:

```bash
npm test
# health ok: {"status":"ok","uptime_seconds":...}
# payment metadata ok
```

Or inline:

```bash
node -e "const {MD2HTMLClient}=require('./md2html-client'); \
  const c=new MD2HTMLClient(); \
  c.health().then(r=>console.log('health',r.status));"
```

## License

MIT — see the [MD2HTML repository](https://github.com/danielbenevides-ops/md2html-api).
