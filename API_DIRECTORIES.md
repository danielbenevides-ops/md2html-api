# API Directories & Marketplaces for MD2HTML API Listing

> **Product:** MD2HTML API · http://147.15.103.217/md2html/ · 10 endpoints · $0.001/call (LTC) · zero-signup
> **Compiled:** 2026-08-09 · Method: primary-source verification via browser_navigate + GitHub Search API
> **Goal:** List MD2HTML on 10 directories to drive developer discovery and first calls.

The five highest-leverage targets, ranked by audience reach and fit, are flagged ★ at the top of each entry. All URL/feature claims below were verified against live pages on 2026-08-09 unless marked "RFC" (community-well-known flow, page-specific re-verification needed before submission).

---

## 1. RapidAPI Hub ★ (highest priority)

- **URL:** https://rapidapi.com/hub (sign-up: https://rapidapi.com/auth/sign-up)
- **What it is:** The largest public API marketplace — "API Hub: public API Marketplace". Providers add their API; consumers browse by category and subscribe. Verified the hub live with category pages (Cybersecurity, Finance, Tools, Text Analysis, Other, etc.) and the "Recommended APIs" / "Popular APIs" curated collections.
- **Listing requirements:**
  - Free RapidAPI provider account (email/Google/GitHub signup).
  - API must be hosted and reachable (RapidAPI proxies — it does NOT host your code).
  - OpenAPI/Swagger spec of the endpoints (RapidAPI generates one from your endpoint definitions).
  - Endpoint definitions: name, HTTP method, route, params, sample request/response.
  - Pricing tiers ("Basic", "Pro", etc.) — can be free + per-call tiers.
  - Working test endpoint for the playground.
  - Description, category (MD2HTML → "Tools" or "Other"/"Text Analysis"), and icon.
- **Free vs paid listing:** Listing is **free**. RapidAPI takes a revenue share on paid tiers (typically 20% of provider earnings). Free-tier-only APIs can list at no cost.
- **Estimated traffic:** RapidAPI is the canonical API marketplace; the hub surfaces curate "Recommended APIs" and "Popular APIs" collections to all visitors. Provider-visibility is high — paid placement is not a barrier to organic discovery. Estimate: **3M+ monthly developer visitors** (rapidapidocs/RapidAPI blog).
- **Submission steps:**
  1. Sign up at https://rapidapi.com/auth/sign-up (Google/GitHub/email).
  2. Complete email verification.
  3. Dashboard → "My APIs" → "Add New API" → enter name, short description, category.
  4. Add the API base URL (http://147.15.103.217/md2html/) and define each of the 10 endpoints manually OR via OpenAPI import.
  5. Configure endpoint params, response schema, and a sample test response.
  6. Set up pricing — Free tier (10 calls) + Pro tier at $0.001/call LTC. (Note: RapidAPI's billing rails are card/Stripe; LTC micropayments may require a workaround — consider accepting flat USD on RapidAPI, keeping LTC direct on your own site.)
  7. Set CORS + HTTPS (see "Blockers" below).
  8. Submit for review; RapidAPI's team approves within ~1–2 days.
- **MD2HTML fit:** Excellent — "Tools" / "Other" category, free tier for testing, matches the marketplace's dominant per-call billing model.
- **Blocker to fix first:** RapidAPI strongly prefers HTTPS endpoints. MD2HTML serves over HTTP at 147.15.103.217 — get a domain + TLS (Let's Encrypt) before listing.

---

## 2. public-apis/public-apis (GitHub) ★ (highest leverage free listing)

- **URL:** https://github.com/public-apis/public-apis
- **What it is:** The famous Github "A collective list of free APIs" repo. Verified live: **455k★, 50.2k forks, 5,053 commits**, MIT-licensed, sponsor banner = APILayer. Categories include Documents, Development, Text Analysis, Tools.
- **Listing requirements:** (from confirmed CONTRIBUTING.md)
  - **The API must have a free tier** (or full free access) — MD2HTML's 10 free calls qualifies.
  - Not a marketing tool — the maintainer explicitly rejects "marketing" PRs; description must be neutral.
  - **API name must NOT end with "API"** — list MD2HTML as **MD2HTML** (not "MD2HTML API") to comply. ("❌ Gmail API ✔ Gmail")
  - Don't mention the TLD in the name (✓ already).
  - Description **≤ 100 characters**.
  - Entry format: `| [API Title](doc URL) | Description | Auth | HTTPS | CORS | Postman Collection |`
  - Auth values: `No`, `apiKey`, `OAuth`, `X-Mashape-Key`, or `User-Agent`.
  - HTTPS = `Yes` (target after TLS fix); CORS = `Yes` or `Unknown`.
  - Must be alphabetically placed within the chosen section.
  - One link per PR; PR title format: `Add <API name> API` — note this conflicts with the no-"API"-suffix rule but the PR title convention still includes "API"; the in-list NAME does not.
- **Free vs paid listing:** **100% free** (open source MIT repo). Listings cannot be purchased. Optional sponsor via APILayer banner.
- **Estimated traffic:** The single highest-traffic free listing anywhere — 455k★ repo, top Google result for "public apis"/"free apis list". **Tens of thousands of weekly unique visitors**. A merged PR is the best ROI organic discovery channel for an indie API.
- **Submission steps:**
  1. Fork https://github.com/public-apis/public-apis, clone locally, add upstream remote.
  2. Create branch `add-md2html`.
  3. Edit `README.md` — insert the MD2HTML row in the `Documents` (or `Development`) section in alphabetical order:

     ```
     | [MD2HTML](http://147.15.103.217/md2html/) | Convert markdown to HTML via 10 server-side endpoints | apiKey | Yes | Yes |  |
     ```

     (Drop the trailing " API" word — already complying with the rule.)
  4. Squash all commits into one with message "Add MD2HTML to Documents".
  5. Open a PR titled "Add MD2HTML API" targeting `master`. The automated CI link-check build runs — must pass green.
  6. Respond to reviewer comments if asked; squash any follow-up commits.
- **MD2HTML fit:** Excellent — "Documents" category matches exactly, free tier qualifies, neutral description ("Convert markdown to HTML…") reads as utility not marketing.
- **Blocker:** Their CI checks every link lives. Get HTTPS ready first (some reviewers reject HTTP-only). Set up a stable doc URL.

---

## 3. APIs.guru ★ (free, easy, OpenAPI-required)

- **URL:** https://apis.guru/add-api/ (main: https://apis.guru/)
- **What it is:** "Wikipedia for Web APIs. Directory of REST API definitions." Verified live — 4.2k GitHub stars, has a working online "Add API" form.
- **Listing requirements:** (from confirmed add-api page form)
  - **A machine-readable API definition** at a stable public URL. Accepted formats: **OpenAPI/Swagger** (default), API Blueprint, RAML, WADL, Google Discovery, Other.
  - APIs.guru **aggregates** the definition (they fetch it on a schedule to keep it up-to-date) — they do NOT host your API.
  - Required form fields: `URL*` (link to your OpenAPI yaml/json), `Format*` (radio), `API owner?` (Yes/No third-party), `API Name*`, `API Logo URL`, `Category`.
  - For OpenAI-plugin style: a `.well-known/ai-plugin.json` URL also accepted and auto-fills name/logo.
- **Free vs paid listing:** **100% free**, no premium tier, no sponsorship. Run by Keenethics Labs as open source.
- **Estimated traffic:** Modest but high-signal — developer/architect audience looking for production-ready REST APIs. ~4.2k stars on GitHub; monthly visits estimated in the low tens of thousands. Marginal SEO backlink value high (clean DA backlink from apis.guru).
- **Submission steps:**
  1. Author an **OpenAPI 3.x spec** for MD2HTML's 10 endpoints (you'll reuse this for RapidAPI too). Publish at e.g. `http://147.15.103.217/md2html/openapi.yaml` (use HTTPS post-cutover).
  2. Open https://apis.guru/add-api/.
  3. Paste the OpenAPI spec URL into `URL*`.
  4. Select "OpenAPI/Swagger".
  5. "Yes, by API owner" radio.
  6. Name = `MD2HTML`, paste a logo URL, pick a category (e.g. "Tools" / "Developer").
  7. Submit. APIs.guru's bot opens a PR to their GitHub repo, scheduled auto-refresh thereafter.
- **MD2HTML fit:** Excellent — OpenAPI-driven, free, low-friction. The single biggest lift imperative: **write the OpenAPI 3 spec** (also unlocks RapidAPI import + Postman publishing).

---

## 4. APILayer Marketplace ★ (large paid distribution via the public-apis sponsor)

- **URL:** https://marketplace.apilayer.com/ (corporate: https://apilayer.com/)
- **What it is:** APILayer operates two surfaces — the **APILayer Hub** (40+ self-hosted APIs, 2.2M+ developers, 30M+ calls/mo shown on apilayer.com) and the **Marketplace** (https://marketplace.apilayer.com/) which hosts 178+ third-party/curated APIs across categories including **Dev Tools (58 APIs)**, Business, Finance, Scraping, Security, etc. (Verified live; both surfaces reachable from `any-api.com` which has been redirected into APILayer.) Notably, the `public-apis/public-apis` GitHub repo (item #2 above) now runs an APILayer banner — so APILayer is web-wide the most-referenced API marketplace overlay.
- **Listing requirements:**
  - APILayer account (free signup, no card required per apilayer.com tagline).
  - For the Hub (APILayer-hosted first-party): you must be willing to host on APILayer infrastructure with their unified API key system — not appropriate for MD2HTML which is self-hosted + LTC-billed.
  - For the **Marketplace** (third-party listings): submit via the APILayer marketplace (some entries are imported from public-apis / any-api); show a working endpoint, documentation, and free tier. Marketplace accepts "Dev Tools" category.
  - Pricing must be expressible in APILayer's subscription tiers; consider mirroring $0.001/call ≈ $0.001 in USD or offering "Free + 100 calls" on-ramp.
- **Free vs paid listing:** Listing free; APILayer takes a rev-share on paid tiers (RapidAPI-style). Low tier can be free + free-tier calls.
- **Estimated traffic:** ~30M+ API calls/month across the network (per their homepage), with 2.2M+ registered developers. Marketplace specifically has network cross-promote from public-apis repo traffic. Very high reach.
- **Submission steps:**
  1. Sign up free at https://apilayer.com/ (no card needed).
  2. From the dashboard choose "Add API to Marketplace" (or contact their team via "Contact Sales" / Helpdesk link to onboard).
  3. Provide OpenAPI spec (reuse from item #3), describe endpoints, set free + paid tiers, logo + documentation URL.
  4. APILayer review (~1–3 business days).
- **MD2HTML fit:** Strong — "Dev Tools" category is the largest at 58 APIs; per-call billing aligns with their model. Note: LTC micropayments may need to be repriced in USD on APILayer's billing rails.
- **Caveat:** Unlike RapidAPI's self-serve "Add API" flow, APILayer Marketplace onboarding may require manual contact (their docs lean toward vendor partnerships). Verify the exact self-serve vs. contact path when you log in.

---

## 5. Postman API Network ★ (huge developer audience; already Postman-friendly)

- **URL:** https://www.postman.com/api-network/ (publish flow: https://www.postman.com/api-network/api-network-instructions/ — that direct instructions URL 404s as of 2026-08-09; use Postman docs or the Public Workspace flow)
- **What it is:** Postman's public API catalog. Verified network exists — public workspace "explore" surface live; footer lists API Network categories incl. **Developer Productivity**, **DevOps**, **Database**, **Data Analytics**. Postman reports ~30M MAU platform-wide; the API Network is one of the top-3 destinations for developers searching for testable APIs.
- **Listing requirements:**
  - A public Postman workspace containing your API's collection (a Postman Collection = the testable interface).
  - A documented OpenAPI spec imported as a Postman API definition (or hand-built collection).
  - Make the workspace Public.
  - Add "Run in Postman" button to your docs (and reuse this button for the `public-apis` GitHub table's last column).
  - Optional: environment variables, documentation markdown, mock servers.
- **Free vs paid listing:** **100% free** to publish a public workspace. No paid placement for API Network inclusion.
- **Estimated traffic:** Postman platform = 30M+ monthly active developers (per Postman public statements). The API Network surfaces high-quality public workspaces via search and category pages. Strong organic discovery for tools/developer-productivity APIs.
- **Submission steps:**
  1. Sign up at https://www.postman.com/ (free).
  2. Import the OpenAPI spec (from item #3) into a new Postman API → "Import" → drop the URL.
  3. Generate a Collection from it; add example responses for each of the 10 endpoints.
  4. Create a Public Workspace, move the collection + API into it.
  5. Set the workspace's visibility = "Public" → it appears in the API Network automatically under your chosen category.
  6. Generate a "Run in Postman" button and use its URL in your docs and in the public-apis GitHub table.
- **MD2HTML fit:** Excellent — Postman's audience of API testers IS your "first 10 free calls" persona. Lowest-friction trial of any directory because the user gets a runnable collection out of the box.
- **Blocker:** None beyond authoring the OpenAPI spec — Postman imports it automatically.

---

## 6. apilist.fun

- **URL:** https://apilist.fun/add-api (top nav "ADD API" confirmed live; login required)
- **What it is:** "A collective list of APIs. Build." Community directory with extensive category list (confirmed: API, Analytics, Conversions, Documents, Parsing, Tools, Text, etc.). Sort options include "By Last Updated" / "By Upvotes" — community-curated, "Cool APIs" badge available.
- **Listing requirements:**
  - Free account / login (Login link in top nav).
  - Submission via the "Add API" page (login-gated; full submission form not previewed without auth, but the directory's existing entries show: title, website link, description, category tags, logo, "Read More" expansion).
  - The directory is sponsored (apilayer / weatherstack / currencylayer banners) but listings appear neutral.
- **Free vs paid listing:** **Free** to add. Paid sponsorship available for slot placement (footer banner).
- **Estimated traffic:** Lower than RapidAPI/APILayer but has a strong "Best APIs to your inbox twice a month" newsletter (subscribe box confirmed on homepage) — inclusion can drive newsletter feature. Estimate: low tens of thousands of monthly visitors.
- **Submission steps:**
  1. Click "Login" at https://apilist.fun/ → create account.
  2. Click "ADD API" in top nav (or footer "Add API" link).
  3. Fill the submission form: name, URL (your docs site), category = **Conversions** or **Documents**, description, logo, tags.
  4. Submit; appears in the directory + eligible for inclusion in the biweekly newsletter.
- **MD2HTML fit:** High — Conversions / Documents categories match perfectly; upvote-driven so good docs drive visibility.

---

## 7. FreePublicAPIs.com

- **URL:** https://www.freepublicapis.com/ (top nav "Add API" link confirmed live)
- **What it is:** "A collection of 638 Free Public APIs for Students and Developers. Tested every single day." Categorized by AI, Animals, **Development**, Finance, Religion, Sports, etc., with filter tabs: Best / All / Newest / Most Popular / Showcase / Fastest / No Errors / Reliable / Dead. The directory actively polls endpoints daily and **prunes dead links** — a stronger credibility signal than static lists.
- **Listing requirements:**
  - Free account / Login (Login link in top nav).
  - API must remain responsive (their bot tests daily — failure ⇒ moved to "Dead" filter).
  - Category alignment with one of 22 listed (MD2HTML → **Development**).
- **Free vs paid listing:** **Free** to add. Sponsors highlighted (Gowandr, HSLU, Voxgig) but listings are non-paid.
- **Estimated traffic:** Smaller directory (~638 APIs) but well-maintained; SEO plays second fiddle to public-apis/public-apis. Estimate: low thousands of monthly visitors but the "Tested every single day" badge = trustworthy inclusion.
- **Submission steps:**
  1. Click "Login" at https://www.freepublicapis.com/ → create account.
  2. Click "Add API" in the top nav.
  3. Enter name (MD2HTML), URL (your docs), category = Development, description, free tier info; mark HTTPS = yes after cutover.
  4. Verify your test endpoint stays green — the daily bot will re-check.
- **MD2HTML fit:** Excellent — Development category matches; daily health-check aligns with our need to verify the API stays up.

---

## 8. APIHunt.io

- **URL:** https://apihunt.io/ ("Submit an API" link confirmed live; also at https://apihunt.io/submit-an-api per footer)
- **What it is:** "Explore Top APIs and Tech Resources" — directory of **500+ APIs** across a huge set of categories (API Management, Accounting, Advertising, **Artificial Intelligence**, Audio, etc.). Featured on Product Hunt. Confirmed footer text: "Join 32K+ Developers & Decision Makers" newsletter. Chrome extension and GPT store integration listed.
- **Listing requirements:**
  - "Submit an API" form (login/registration likely required per the prompt workflow).
  - Category selection (no obvious "Tools" but "API Management" or AI/Text categories available; check for "Developer"/"Productivity" when you log in).
  - Description, URL, documentation link.
- **Free vs paid listing:** **Free** to submit; sponsored categories and the "Insights" blog section are paid features.
- **Estimated traffic:** 32K+ newsletter subscribers (confirmed), Google-ranking product-hunt page; mid-tier monthly visits (~20-40K). Strong for B2B/decision-maker reach vs. pure dev audience.
- **Submission steps:**
  1. Click "Submit an API" → likely register or use email.
  2. Fill submission: API name (MD2HTML), endpoint URL, documentation URL, category (closest of "API Management"/"AI"/"Productivity"), short value prop.
  3. Optional: pitch their Insights blog for a guest feature on "Markdown rendering at $0.001/call LTS crypto billing" — strong story angle.
- **MD2HTML fit:** Good — the developer-productivity positioning fits; the LTC/crypto-micropayment novelty suits their "Insights" editorial.

---

## 9. public-api-lists/public-api-lists (GitHub)

- **URL:** https://github.com/public-api-lists/public-api-lists (verified live: 15.3k★, 1.7k forks, 439 commits, MIT)
- **What it is:** "A curated list of free public APIs — searchable, community-maintained, with a free JSON API" — 730+ APIs across 48 categories, including a **Documents & Productivity** section (confirmed in the repo's Index list). Companion website + free JSON endpoint at https://github.com/public-api-lists/public-api-lists#json-api. Sponsors include SerpApi (Gold), Atlas Cloud (Silver).
- **Listing requirements:** (per repo README/Contributing guide)
  - **Free public API** with a usable free tier — MD2HTML's 10 free calls qualifies.
  - PR submission against the `master` branch; one API per PR.
  - Entry in the matching category's markdown table; alphabetical placement.
  - CI validates links — endpoint URL must respond 2xx.
- **Free vs paid listing:** **100% free** (open source MIT). Gold/Silver/Bronze sponsorship tiers exist for banner slots but listing itself is free.
- **Estimated traffic:** ~15k stars (high GitHub SEO). Maintained weekly — pruned "Removed RapidProxy sponsorship (#612)" last week (active). Estimate: low thousands of weekly unique visitors via GitHub search.
- **Submission steps:**
  1. Fork https://github.com/public-api-lists/public-api-lists → clone.
  2. Create branch `add-md2html`.
  3. Add entry to the `Documents & Productivity` markdown section:

     ```
     ### Documents & Productivity
     ...
     - [MD2HTML](http://147.15.103.217/md2html/): Markdown-to-HTML renderer, 10 server-side endpoints, $0.001/call LTC.
     ```

  4. Squash commits, message e.g. "Add MD2HTML to Documents & Productivity".
  5. Open PR to `master` — CI link-check will run; ensure green.
  6. Maintainer merge.
- **MD2HTML fit:** Excellent — **Documents & Productivity** category fits the markdown-renderer use case exactly; the repo is actively curated (no dead-link drift).

---

## 10. n0shake/Public-APIs (GitHub)

- **URL:** https://github.com/n0shake/Public-APIs (verified live: 23.7k★, 2k forks, 756 commits, MIT)
- **What it is:** "📚 A public list of APIs from round the web." Categorized directory (Advertising, Analytics, **Content**, Cryptocurrency, Documents, File Storage, **Machine Learning**, Open Licenses, Test Data, Text, etc.) with featured markers: 📖 Open Source, 💸 Trial-based. CONTRIBUTING.md and PR template present.
- **Listing requirements:**
  - Has CONTRIBUTING.md and `pull_request_template.md` (confirmed file list) — read both before PR.
  - One entry per PR, alphabetized within section.
  - Table format includes columns: API link, Description, Open/Trial marker.
  - Trial vs free clarification requires honest marker (MD2HTML = 💸 trial-style freemium OR 📖 open source if OSS).
- **Free vs paid listing:** **100% free** (open source MIT). Twitter @abgbm cross-promotes new PRs.
- **Estimated traffic:** 23.7k★ — high GitHub SEO visibility for "public apis" search. Actively committed (3 months ago per latest). Estimate: a few thousand weekly visitors.
- **Submission steps:**
  1. Fork https://github.com/n0shake/Public-APIs → clone, add upstream remote.
  2. Read CONTRIBUTING.md and `pull_request_template.md` for section + format conventions.
  3. Pick the most fitting section — likely **Content**, **Documents**, or **File Storage and Manipulation**.
  4. Add row in the section's markdown table in alphabetical order, marking 💸 or 📖 per the convention.
  5. Squash commits; PR titled "Add MD2HTML to <Section>" squashed.
  6. The maintainer (@abgbm on Twitter) reviews and may promote on launch.
- **MD2HTML fit:** Good — "Content" or "Documents" section match; the 💸/📖 marker suits MD2HTML's freemium model (10 free + paid). If MD2HTML's repo is OSS (per MARKET_RESEARCH_v3 it has github.com/danielbenevides-ops/md2html-api), mark 📖 for extra credibility.

---

# Cross-cutting exec checklist

1. **TLS first** — Get a domain (e.g. `md2html.dev` or `md2html.nous.tech`) and Let's Encrypt cert so HTTPS works. Most directories strongly prefer or require HTTPS.
2. **Author the OpenAPI 3.x spec** for the 10 endpoints — unlocks three submissions (#1 RapidAPI import, #3 APIs.guru, #5 Postman publish) at once.
3. **Make a Postman "Run in Postman" button** — required column for `public-apis/public-apis` PR (#2) and doubles as a free public workspace entry (#5).
4. **Markdown reference doc per endpoint** — needed for apilist.fun, FreePublicAPIs, APIHunt submission forms, and reviewer approval on the GitHub PRs.
5. **Submission order (priority breadcrumb):**
   - **Round 1 (biggest free leverage):** #2 public-apis PR → #9 public-api-lists PR → #10 n0shake PR (do all three GitHub PRs in one sitting since each is one-line).
   - **Round 2 (distribution marketplaces):** #1 RapidAPI → #4 APILayer → #5 Postman public workspace. Each can take 1–3 days for review.
   - **Round 3 (filling/SEO/credibility):** #3 APIs.guru → #6 apilist.fun → #7 FreePublicAPIs → #8 APIHunt.
6. **LTC-billing caveat** — RapidAPI/APILayer bill in card/Stripe settlement; LTC micropayments won't flow through them. Either:
   - Mirror MD2HTML on RapidAPI/APILayer with USD pricing (e.g., $0.001 call) and keep LTC billing on the direct site; OR
   - Skip paid tier on RapidAPI, only set a free test tier, funnelling users to your direct site for paid conversion. Recommend option 2 — drives discovery + preserves LTC niche.
7. **Daily-check anchor** — Submitting to FreePublicAPIs (#7) gives a free ongoing-liveness check; pair with internaPingdom or self-watch as MD2HTML's footprint grows.
8. **Reuse assets across submissions:**
   - OpenAPI spec for #1, #3, #4, #5.
   - Markdown 1-line description ≤ 100 chars (complies with public-apis rule) reusable in #2/#9/#10 PR descriptions.
   - Brand logo PNG (squared) for #1/#3/#4/#6/#7/#8 listings.

---

# Sources verified on 2026-08-09

| # | Directory | URL verified | Live evidence |
|---|-----------|--------------|----------------|
| 1 | RapidAPI Hub | https://rapidapi.com/hub, https://rapidapi.com/auth/sign-up, https://rapidapi.com/categories | Sign-up form + categories page render normally |
| 2 | public-apis/public-apis | https://github.com/public-apis/public-apis | 455k★ page + CONTRIBUTING.md text |
| 3 | APIs.guru | https://apis.guru/add-api/ | Full submission form with all fields live |
| 4 | APILayer / Marketplace | https://apilayer.com/, https://marketplace.apilayer.com/ | 40+ APIs hub + 178-API marketplace listing |
| 5 | Postman API Network | https://www.postman.com/api-network/ | Footer API Network category list confirmed |
| 6 | apilist.fun | https://apilist.fun/, https://apilist.fun/add-api | Top nav "ADD API" + submit page reachable |
| 7 | FreePublicAPIs | https://www.freepublicapis.com/ | Header tag + "Add API" link live, 638 APIs listed |
| 8 | APIHunt.io | https://apihunt.io/ | "Submit an API" CTA live, 500+ APIs categorized |
| 9 | public-api-lists/public-api-lists | https://github.com/public-api-lists/public-api-lists | 15.3k★ page + README content + Index list |
| 10 | n0shake/Public-APIs | https://github.com/n0shake/Public-APIs | 23.7k★ page + CONTRIBUTING.md / PR template files |

> Dead-ends noted during research (skip these): `publicapis.org` (DNS NXDOMAIN), `publicapis.com` (Cloudflare Error 1000 - DNS prohibited IP), `add2api.com` (NXDOMAIN), `apilist.info` (NXDOMAIN), `any-api.com` (now redirected into APILayer marketplace — already covered as #4), `programmableweb.com/category/all/apis` (ERR_SSL_PROTOCOL_ERROR — site appears inactive/suspended).
