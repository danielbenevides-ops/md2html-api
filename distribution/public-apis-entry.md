# public-apis/public-apis contribution artifact

## Proposed table row

This is the review-ready row for the current service state:

```markdown
| [MD2HTML](https://147.15.103.217.sslip.io/md2html/) | Convert Markdown to HTML and provide developer utilities | apiKey | Yes | Yes |  |
```

Columns are `API`, `Description`, `Auth`, `HTTPS`, `CORS`, and `Postman Collection`, respectively. The description is 56 characters.

## Rationale against the current rules

- **Free access:** The repository documents 10 free calls per client, with no signup required for the free tier (`README.md`; `docs/API_REFERENCE.md`). This meets the public-apis free-access requirement.
- **Name:** `MD2HTML` does not end in `API` and does not include a top-level domain.
- **Neutral description:** The 56-character description states the utility without marketing claims and stays below the documented 100-character limit.
- **Authentication:** `apiKey` reflects the documented optional `X-API-Key` mechanism. Requests without a key fall back to client-IP identification, so the free tier remains usable without signup.
- **CORS:** `server.py` sends `Access-Control-Allow-Origin: *` and handles `OPTIONS` preflight requests, supporting `Yes` in the CORS column.
- **Link count:** The row has one service link and no Postman link. No public Postman collection URL is documented in this repository, so the final cell is intentionally blank.
- **Section/order:** The service is a candidate for the `Documents` section because its primary function is Markdown-to-HTML conversion. The row must be placed alphabetically in the upstream section when a PR is prepared.
- **Stale count avoided:** Older local distribution notes propose “10 server-side endpoints,” while the current `docs/API_REFERENCE.md` describes 18 endpoints and `server.py` exposes a broader manifest. The row therefore avoids an unstable endpoint count.

## Verified link and HTTPS state

- **Current service URL:** `https://147.15.103.217.sslip.io/md2html/`
- **Current HTTPS value:** `Yes` — the live service has a valid Let's Encrypt certificate and TLS 1.3 was verified externally.
- **Merge risk:** Upstream maintainers still decide whether the service fits current listing policy. Do not claim acceptance before the PR is merged.
- **Required follow-up:** Refresh the fork against upstream, run its tests, and submit exactly one PR.
