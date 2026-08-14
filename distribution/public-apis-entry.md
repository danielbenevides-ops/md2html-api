# public-apis/public-apis contribution artifact

## Proposed table row

This is the review-ready row for the current service state:

```markdown
| [MD2HTML](http://147.15.103.217/md2html/) | Convert Markdown to HTML and provide developer utilities | apiKey | No | Yes |  |
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

## Link and HTTPS blocker

- **Current service URL:** `http://147.15.103.217/md2html/`
- **Current HTTPS value:** `No` — the live service is HTTP-only. This row deliberately does not claim HTTPS support.
- **Merge risk:** The local `API_DIRECTORIES.md` notes that public-apis expects HTTPS to be available (`HTTPS: Yes`) and warns that link checking and reviewer policy may reject an HTTP-only entry. HTTPS may therefore block merge even though the API otherwise fits the documented rules.
- **Required follow-up:** Put the service behind a stable HTTPS URL with a valid TLS certificate, then replace the link and `No` with the verified HTTPS URL and `Yes` before submission. No external service was contacted while preparing this artifact.
