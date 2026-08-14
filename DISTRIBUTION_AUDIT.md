# Distribution audit

**Scope:** current repository docs and the live public deployment, checked 2026-08-11. This is an audit only; no existing documentation was changed. Priorities reflect likely loss of qualified first calls or rejected submissions.

## Observed contract

- `GET http://147.15.103.217/md2html/health` returned `200`, version `1.4.0`, and **26** advertised routes.[1]
- The live `swagger.json` returned OpenAPI `3.0.3`, version `1.4.0`, with **25** paths. Its path set is not identical to `/health`: it omits `/webhook/register` and `/webhook/test`, while `/health` does not count `/swagger.json`.[5]
- The live usage guide presents `GET /register` as the no-body key-minting flow and says billed requests use `X-API-Key`; the live pricing response says 10 free calls, then `$0.001 USD` with `currency: LTC`, a 30/60-second rate limit, and a 1 MiB body cap.[6][7]

## Corrections, prioritized

### P0 — Replace the stale endpoint inventory with one canonical count

**Files/claims:** `API_DIRECTORIES.md:3,29,86,133,252-254`; `docs/API_REFERENCE.md:1-3,94-115`; older distribution copy such as `distribution/public-apis-entry.md:22`.

These documents alternately describe 10, 18, and an implied older v1.3 contract. The live service is v1.4.0 with 26 advertised product routes.[1] Replace every count/version with the current inventory, and distinguish the 26 product routes from operational routes (`/swagger.json`, `/`, `/index.html`, `/uptime`, and `OPTIONS`). Directory submissions should be generated from that inventory, not hand-counted examples.

**Acquisition impact:** stale counts make marketplace listings and directory reviews look abandoned and cause prospects to miss the newer utility endpoints.

### P0 — Make the submitted OpenAPI document match the live service

**Files/claims:** `API_DIRECTORIES.md:78-93,252`; `DISTRIBUTION_GAP.md:3-5`; `DISTRIBUTION_SNIPPETS.md:19-23`; `openapi.yaml`.

Do not call the spec “the” complete API contract until parity is checked. The live spec has 25 paths and omits both webhook routes present in the live health manifest; the repository’s separate `openapi.yaml` is not the same artifact as the live `/swagger.json`. Add every supported path/method to the published spec, or explicitly label it as a core subset and remove “all endpoints” language. Re-run a path/method diff against `/health` before submitting to APIs.guru, RapidAPI, or Postman.

**Acquisition impact:** directory imports are the highest-leverage accountless distribution path; an incomplete import produces broken or invisible features at the first trial.

### P0 — Fix copy-paste route and method examples before publishing social or directory links

**Files/claims:** `distribution/hn_showhn.md:5-12`; `distribution/reddit_sideproject.md:13,40-44`.

The live `POST /md2html/` and `GET /md2html/?md=...` probes returned `404`. The conversion call is `POST /md2html/convert` with JSON such as `{"markdown":"# Hello"}`; the root path is a landing page, not a conversion endpoint. Replace the examples with a tested request and response. Also remove “no rate limits (yet)”: the deployed service enforces 30 requests per minute per source IP (`server.py:20-25`).

**Acquisition impact:** a new visitor following either post currently gets a 404 or a false capability claim instead of a successful first call.

### P0 — Normalize registration and authentication instructions

**Files/claims:** `distribution/devto_article.md:35-51,61-70`; `INTEGRATION.md:14-33`; any copied snippets using `Authorization: Bearer`.

The public no-friction flow is `GET /register`, followed by `X-API-Key`. Live `POST /register` with no body or with only `email` returned `400 Missing 'email' or 'plan' field`; the POST form therefore needs both `email` and `plan` if it is intentionally documented. Replace all email-only POST examples and all Bearer examples with either the tested GET flow or a tested JSON POST containing both required fields. Keep the optional-IP-billing path visible so “no signup” remains accurate for the free trial.

**Acquisition impact:** registration is the first conversion step after discovery; a 400 caused by copied instructions abandons the lead immediately.

### P0 — Remove the invented Dev.to implementation and settlement story

**File/claims:** `distribution/devto_article.md:17-28,41-51,61-78`.

The repository implements a Python stdlib `http.server` service with JSON/file-backed usage and analytics (`server.py`, `billing.py`, `analytics.py`), not FastAPI + Redis + Litecoin Core. The deployment exposes one wallet address; it does not mint a unique LTC deposit address per user. The separate `check_payments.py` script has a configurable account and defaults to `ltc_payer`; it is not the live HTTP registration contract. Rewrite the tutorial around the actual stack and tested `GET /register`/`X-API-Key` flow, or mark the article as fictional instead of presenting it as a build report.

**Acquisition impact:** technical readers who follow the tutorial will fail at registration and lose trust in the product and repository.

### P1 — Remove unsupported audience, traffic, conversion, and approval estimates

**Files/claims:** `API_DIRECTORIES.md:24,33,55,84,107,112,121,129,151,170,183,189,208,237` and similar “highest ROI,” “strong reach,” or “will drive” language.

Stars/forks are not visitor counts, conversions, revenue, newsletter reach, or an approval SLA. Remove claims such as “3M+ monthly visitors,” “tens of thousands weekly,” “32K+ newsletter,” “30M+ calls/month,” “30M MAU,” and “approval within 1–3 days” unless each is tied to a current first-party source and date. The GitHub API can support current repository metadata such as stars/forks, but not traffic or acquisition outcomes.[4] Use “potential discovery; traffic and review timing unverified” instead of forecasts.

**Acquisition impact:** unsupported numbers are especially damaging in curator review and make the distribution plan look promotional—the exact rejection reason called out by the public-apis contribution rules.[2][3]

### P1 — Keep HTTPS/CORS status truthful and gate submissions on real TLS

**Files/claims:** `API_DIRECTORIES.md:32,35,51,70,251`; `distribution/public-api-lists/README.md:418`; `DISTRIBUTION_SNIPPETS.md:14-22`.

The current public URL is HTTP-only, so current directory rows should say `HTTPS: No`; do not write `Yes` as a future target. The live CORS preflight returned `204` with `Access-Control-Allow-Origin: *`, so `CORS: Yes` is supported. Keep the public-api-lists five-column row format and its current `No | No | Yes` values until a real HTTPS hostname and certificate are deployed, then re-probe before changing the row.[3]

**Acquisition impact:** secure-directory crawlers and browser users need a stable, verifiable URL; advertising future HTTPS as present creates broken links and rejected PRs.

### P1 — Rephrase payment copy to match the live contract

**Files/claims:** `API_DIRECTORIES.md:3,31,105-113,259-261`; `distribution/hn_showhn.md:5,21-25`; `distribution/devto_article.md:28,76-78`.

Use the precise promise: **10 free billable calls per IP or API key; after exhaustion, billable POSTs return `402` with LTC payment information**. Do not claim that every request immediately deducts from a user wallet, that users receive unique deposit addresses, or that an HTTP balance is automatically topped up. The live pricing endpoint exposes a shared wallet/payment instruction, while credit processing is a separate repository operation.[7] If automatic per-user settlement is not live and tested, omit it from directory teasers and launch copy.

**Acquisition impact:** clear payment semantics reduce first-trial confusion and avoid a high-trust failure immediately after the free tier.

## Sources

[1] http://147.15.103.217/md2html/health — MD2HTML live health endpoint

[2] https://raw.githubusercontent.com/public-apis/public-apis/master/CONTRIBUTING.md — public-apis current contributing guide

[3] https://raw.githubusercontent.com/public-api-lists/public-api-lists/master/.github/CONTRIBUTING.md — public-api-lists current contributing guide

[4] https://api.github.com/repos/public-apis/public-apis — public-apis GitHub repository metadata

[5] http://147.15.103.217/md2html/swagger.json — MD2HTML live OpenAPI document

[6] http://147.15.103.217/md2html/docs — MD2HTML live usage guide

[7] http://147.15.103.217/md2html/pricing — MD2HTML live pricing endpoint
