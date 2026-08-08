# Analytics Report

**Generated:** 2026-08-08
**Source:** `md2html` API live endpoints (`/stats`, `/usage`)

## Current Metrics

| Metric | Value |
|---|---|
| **Total Calls** | 217 |
| **Unique IPs** | 1 |
| **Average Latency** | 0.001s (~1ms) |

### Calls by Endpoint

| Endpoint | Calls |
|---|---|
| `/convert` | 79 |
| `/health` | 23 |
| `/` | 23 |
| `/register` | 20 |
| `/json/prettify` | 18 |
| `/slug` | 16 |
| `/text/stats` | 14 |
| `/stats` | 7 |
| `/docs` | 6 |
| `/usage` | 5 |
| `/payment` | 5 |
| `/pricing` | 1 |

### Usage (client `127.0.0.1`)

- Calls made: 29
- Free tier limit: 10
- Remaining: 0 (limit exceeded)

## What We Need to Track

We currently capture call counts, IP, endpoint, and latency. The following metrics are blind spots:

1. **Referral source** — Where users discover the API (HTTP `Referer` header, UTM params, or partner IDs).
2. **Conversion rate** — Percentage of `/pricing` or `/docs` visitors who proceed to `/register` and a paid `/convert` call.
3. **Paid vs. free calls** — We log free-tier usage but don't tag individual calls as paid/free in the stats endpoint, blurring the revenue picture.
4. **Error/ failure rate** — All calls are counted equally; we don't track HTTP 4xx/5xx responses separately to measure reliability.
5. **User retention / repeat usage** — No per-IP or per-API-key call frequency over time, so we can't distinguish one-time users from active subscribers.

---

*Word count: ~295*
