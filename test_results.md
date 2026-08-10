# LinkPeek API QA Test Results

**Base URL:** http://147.15.103.217.sslip.io
**Test input URL:** https://github.com
**Test run:** 2026-08-09 21:23:01 UTC

| # | Endpoint | Path | HTTP Status | Response Time (s) | Body Size | Valid Body | Result |
|---|----------|------|------------|-------------------|-----------|-----------|--------|
| 1 | preview | `/api/preview?url=https%3A%2F%2Fgithub.com` | 200 | 0.400 | 0B | NO (empty body) | **FAIL** |
| 2 | qr | `/api/qr?url=https%3A%2F%2Fgithub.com` | 400 | 0.283 | 0B | NO (empty body) | **FAIL** |
| 3 | health | `/api/health` | 200 | 0.279 | 0B | NO (empty body) | **FAIL** |
| 4 | word-count | `/api/word-count?url=https%3A%2F%2Fgithub.com` | 200 | 0.355 | 0B | NO (empty body) | **FAIL** |
| 5 | shortlink | `/api/shortlink?url=https%3A%2F%2Fgithub.com` | 200 | 0.288 | 0B | NO (empty body) | **FAIL** |
| 6 | tech-stack | `/api/tech-stack?url=https%3A%2F%2Fgithub.com` | 200 | 0.648 | 0B | NO (empty body) | **FAIL** |
| 7 | readability | `/api/readability?url=https%3A%2F%2Fgithub.com` | 200 | 0.384 | 0B | NO (empty body) | **FAIL** |
| 8 | screenshot-url-hint | `/api/screenshot-url-hint?url=https%3A%2F%2Fgithub.com` | 200 | 0.270 | 0B | NO (empty body) | **FAIL** |
| 9 | ssl-info | `/api/ssl-info?url=https%3A%2F%2Fgithub.com` | 200 | 0.362 | 0B | NO (empty body) | **FAIL** |
| 10 | dns-lookup | `/api/dns-lookup?url=https%3A%2F%2Fgithub.com` | 200 | 1.026 | 0B | NO (empty body) | **FAIL** |
| 11 | og-image | `/api/og-image?url=https%3A%2F%2Fgithub.com` | 400 | 0.302 | 0B | NO (empty body) | **FAIL** |
| 12 | uuid | `/api/uuid` | 200 | 0.276 | 0B | NO (empty body) | **FAIL** |
| 13 | hash-text | `/api/hash-text?text=hello` | 200 | 0.286 | 0B | NO (empty body) | **FAIL** |
| 14 | password-strength | `/api/password-strength?password=Test1234!` | 200 | 0.304 | 0B | NO (empty body) | **FAIL** |
| 15 | cron-parser | `/api/cron-parser?expr=0%209%20*%20*%20*` | 200 | 0.308 | 0B | NO (empty body) | **FAIL** |

## Summary

- **Total endpoints tested:** 15
- **Passed:** 0
- **Failed:** 15
- **Pass rate:** 0%

## Notes
- All endpoints hit with sample input `https://github.com` where a URL parameter is accepted.
- `/api/qr` returns a PNG image binary; validity = non-empty, 2xx response.
- `/api/uuid`, `/api/hash-text`, `/api/password-strength`, `/api/cron-parser` do not take a URL.
- Response time is wall-clock from curl start to body receipt.
