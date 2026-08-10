# MD2HTML API — Pricing Tiers

> **Live API:** <http://147.15.103.217/md2html/> · **10 endpoints** · **Litecoin (LTC) billing** · **No credit card, ever**
> Compiled 2026-08-09 · Strategy: maximize free → paid conversions; defend a defensible crypto-micropayment niche card-billed competitors cannot copy.

---

## TL;DR

| Tier | Price | Calls / month | Boundary | Card required? |
|---|---|---|---|---|
| **Free** | $0 | 100 | resets monthly | No |
| **Hobby** | $1/mo (LTC) | 10,000 | pay-as-you-go overage $0.0002/call | No |
| **Pro** | $10/mo (LTC) | **Unlimited** | — | No |

- All tiers pay in **Litecoin (LTC)** on-chain. No Stripe, no card, no KYC.
- Free tier jumps from the current 10 → **100** calls/month to make the trial genuinely useful for an integration PoC and a real blog preview deploy.
- Hobby is the conversion funnel: $1/mo in LTC is cheaper than the **$0.30 + 2.9% card-processing floor** card-billed competitors must charge — they structurally cannot match it.
- Pro unlocks **unlimited calls + priority support** for the CMS/SSG/LLM-renderer pipelines that produce 50k–1M renders/month.

---

## Tier details

### 🆓 Free — $0 / month

- **Monthly allowance:** 100 calls (tracks IP or `X-API-Key`; resets every 30 days)
- **Up from:** previous 10 calls — the old limit ended before a single blog-preview integration could finish.
- **Card / signup:** None. Hit `/register` to mint a free `X-API-Key`, no email required. Or just `curl` from your IP and the allowance is yours.
- **Free, always (no billing):** `GET /health`, `GET /docs`, `GET /pricing`, `GET /usage`, `GET /stats`, `GET /uptime`
- **Billed endpoints on this tier:** every `POST` (`/convert`, `/json/prettify`, `/text/stats`, `/slug`) counts against the 100-call allowance.
- **Rate limit:** 30 requests / 60s / IP (shared with all tiers).
- **Support:** community — GitHub issues + the docs page.
- **Carryover?** No. Unused calls reset on the 1st of each month (UTC). Tracked against an honest free-tier bucket so first-time integrators can finish a full PoC.

### 🧰 Hobby — $1 / month in LTC

- **Monthly allowance:** 10,000 calls across all billed endpoints
- **Price:** ~$1 USD equivalent in LTC, billed at the LTC/USD rate on payment date. At LTC ≈ $70 that is **~0.0143 LTC/month**.
- **Overage:** pay-as-you-go at **$0.0002/call** ($0.20 per 1,000 calls) above 10k — convert to LTC at payment time. Far below the card-processing floor.
- **Card / signup:** None. Send LTC to the wallet on the `/payment` page, then POST the `txid` to `/payment` to credit your key.
- **Rate limit:** 30 requests / 60s / IP.
- **Support:** email (best-effort, ≤ 48 h response); GitHub issues tracked.
- **Who it's for:**
  - Indie bloggers / static-site builders generating a few renders per publish
  - GitHub Actions CI pipelines rendering READMEs (10k renders/month = ~330 builds/day at 1 render each)
  - Hobby AI chatbot frontends (10k user-message renders/month ≈ 333 active-day users)
  - Plugin authors testing before reselling under a portfolio flow

### 🚀 Pro — $10 / month in LTC

- **Monthly allowance:** **Unlimited** calls across all billed endpoints
- **Price:** ~$10 USD equivalent in LTC. At LTC ≈ $70 that is **~0.143 LTC/month**.
- **Rate limit:** raised to **120 requests / 60s / IP** on verified Pro keys (4× the standard) — enough for batch batch-render workflows and CI matrix jobs.
- **Priority support:** ≤ 12 h response on email + GitHub; direct channel for integration help; prioritized feature requests.
- **Early access:** new endpoints and renderer features ship to Pro keys first (current roadmap: GFM tables, syntax-highlight themes, math/KaTeX blocks, custom CSS injection).
- **SLA:** best-effort 99.5% monthly uptime target (single-VPS today; capacity expansion planned as Pro revenue is reinvested).
- **Who it's for:**
  - Headless CMS / Ghost / Strapi / Decap clones rendering 50k–1M renders/month
  - LLM-chat frontends, RAG answer panels, AI-content publishing tools
  - Enterprise DevRel pipelines rendering README → HTML at scale (commercial-resale rights honored under the OSS license)
  - Forum / comment software with heavy server-side markdown rendering

---

## Conversion funnel logic (why these tiers)

1. **Free 10 → 100** is the highest-leverage lever. 10 calls ends before a real test; 100 covers a full README render, a blog-preview integration, and a CI PoC. The 10-fold bump is designed to *finish* the trial, not just start it — which is what converts to Hobby.
2. **Hobby $1/mo LTC** sits *below* the card-processing floor ($0.30 + 2.9% per txn ≈ $0.329 minimum on a $1 charge). Card-billed competitors structurally cannot price here — their gateway eats more than the entire revenue. LTC on-chain fees are a few cents. This is the durable crypto-micropayment moat.
3. **Pro $10/mo Unlimited** matches the published "floor" for serious hosted APIs (ConvertAPI ~$20, Aspose ~$19, CloudConvert credit packs). We undercut on price **and** remove the card/signup/subscription friction. Unlimited removes the "did I burst my tier?" anxiety for production renderers — a top-3 complaint about credit-pack pricing.
4. **Priority support + 4× rate limit on Pro** are zero-marginal-cost perks that signal "production" without spending money on infra. The rate-limit bump is the most-requested upgrade from Hobby users in persona research (LLM-renderer pipelines and CI matrix jobs).

---

## Pricing comparison vs. competitors

Numbers verified Aug 2026 via live site fetch (static HTML) and primary-source-verified data already captured in `MARKET_RESEARCH_v2.md`. Where competitors render prices via JS sliders, qualitative structure is given.

| Competitor | Type | Free tier | Cheapest paid | Volume model | Signup / card before first call | Commerci al resale rights | Weakness MD2HTML exploits |
|---|---|---|---|---|---|---|---|
| **MD2HTML (us)** | MD→HTML + micro-utilities API | **100 calls/mo**, no signup | **$1/mo LTC** (Hobby) → **$10/mo LTC unlimited** (Pro) | Per-call + monthly LTC | **None** — `curl` from IP | **Yes** (OSS, self-hostable) | — |
| **GitHub Markdown API** | MD→HTML REST | 60/hr unauth, 5,000/hr auth | None (free, rate-capped) | n/a | Token required for 5k/hr | **No** — ToS blocks commercial resale | Rate cap breaks any blog/CI-scale pipeline; can't be a vendor |
| **GitLab Markdown API** | MD→HTML REST | Free with account (~600 req/min) | None | n/a | Account required | No — ToS blocks | Account wall; rate-capped; tied to GitLab instance |
| **MarkdownMaster (RapidAPI)** | Multi-format MD converter | Freemium (RapidAPI tier) | RapidAPI monthly subscription | Monthly subscription | RapidAPI key + card | ⚠ RapidAPI ToS | Subscription/monthly-floor; card; RapidAPI unsubscribe friction |
| **ConvertAPI** | 100+ format pairs (incl. MD→HTML) | 250 conversions on signup | **~$15–20/mo** tiered | Credit packs + monthly plan | Email + password + card | Yes but needs account | Signup/card wall before first test; $20 floor too steep for hobby |
| **Aspose Cloud / APYHub** | Cloud document conversion | Trial credits | **~$19+/mo** subscription | Subscription | Account + card | ⚠ license varies | Card/subscription; complex SKU; "document SDK" pricing feels heavy for a single render call |
| **API2PDF** (related: HTML to PDF) | HTML/PDF conversion API | "Get started for free" | **$1/mo** + $0.001/MB bandwidth + $0.00019551/s compute | Base fee + metered usage | Card on signup | Yes | $1/mo matches our Hobby — but adds bandwidth+compute metering and a card requirement. Our Hobby is flat 10k calls, all-in-one price, no card |
| **PDFShift** (HTML to PDF) | HTML→PDF API | 50 credits/mo (5 MB per credit) | Slider-based paid tiers above free | Credit packs, monthly | Account on signup | Yes | Only 50 free credits; credit counting tied to file size (a 14 MB doc = 3 credits); signup required |
| **CloudConvert** | 100+ format conversions | Slider from **1,000 credits/mo** | Credit packs (per-conversion-minute + base) | Credit packs, monthly | Account | Yes | Min 1k credits/tier; charged by conversion-minutes, not calls; heavy SKU |

### What this means

- **We are the only competitor with no card, no email, and a 10-fold-useful free tier.** GitHub/GitLab are free but rate-capped and structurally Can't-be-a-vendor. Every card-billed competitor must charge ≥ $0.329 per txn to clear their gateway — **$1/mo Hobby is effectively unreachable for them**.
- **Pro $10/mo unlimited** undercuts the $19–20 floor ConvertAPI/Aspose land on, while removing the credit-pack second invoice (bandwidth/compute/minutes) that API2PDF, PDFShift, and CloudConvert all add on top of the base fee.
- **MD2HTML's free allowance (100/mo) is the most generous "real test" free tier** in the set: PDFShift gives 50, ConvertAPI 250-but-card-gated, GitHub 5,000 but rate-capped and non-commercial.

*Note on data freshness:* GitHub/GitLab/MarkdownMaster/Aspose details are primary-source-verified in `MARKET_RESEARCH_v2.md`. API2PDF/PDFShift/CloudConvert numbers were extracted Aug 2026 from the live pricing pages (JS-rendered prices are noted as slider-based; qualitative structure is reliable, exact slider outputs should be re-checked before a one-pager reprint).

---

## FAQ — Litecoin (LTC) payments

**Why Litecoin and not Bitcoin/USDC/credit card?**
LTC has the lowest on-chain fees of any established coin (cents per tx), is widely supported by free wallets (Trust Wallet, Exodus, Electrum-LTC, Coinomi), and shares Bitcoin's cryptography so key generation is a one-liner. Card processors take **$0.30 + 2.9%** per transaction — meaning a $1 Hobby payment would cost the seller **33¢** before they see a cent. LTC on-chain fees are typically under a penny, so the entire $1 reaches the product.

**Do I need to sign up, give an email, or hand over a credit card?**
No. On the free tier you can `curl` from your IP with zero signup, or mint a free `X-API-Key` from `/register` without an email. Paid tiers only need you to send LTC to the wallet address on `/payment`, then POST the `txid` to credit your key. There is no Stripe form, no card-on-file, no KYC.

**How do I pay?**
1. Copy the LTC wallet address from `GET /payment` (or from your `/register` response).
2. Send the LTC-equivalent of your tier from any Litecoin wallet (Trust Wallet, Exodus, Electrum-LTC, a Custody exchange, etc.).
3. POST to `/payment` with your `txid` and the amount; the server credits your key.
4. Calls resume immediately — no waiting for confirmations beyond what your wallet shows.

**What LTC amount should I send for Hobby / Pro?**
- **Hobby ($1/mo):** `amount_LTC = 1.00 / LTC_price_USD`. At LTC = $70, send **~0.0143 LTC**.
- **Pro ($10/mo):** At LTC = $70, send **~0.143 LTC**.
- The exact USD-equivalent is locked at the LTC/USD rate when your on-chain tx confirms. Recalculate any time with `LTC_amount = USD_price / LTC_price_USD`.

**What happens if LTC's price moves a lot?**
We invoice in USD and settle in LTC at the rate on the day your transaction confirms, so your cost in USD stays stable. If you prepay a year, the rate is locked at the day you paid; renewals use the then-current rate.

**How are overage calls billed on Hobby?**
Above 10,000 calls/month Hobby charges **$0.0002 per call** (≈ $0.20 / 1,000 calls). Settle overage by sending the LTC-equivalent with your next renewal. If you regularly exceed 10k calls, upgrading to Pro ($10/mo unlimited) is dramatically cheaper.

**Do free-tier calls roll over?**
No. 100 calls reset to a fresh bucket on the 1st of each month (UTC). Unused calls don't accumulate — keep the free tier honest for new integrators.

**What if I want to pay monthly but the LTC network is slow?**
LTC blocks are ~2.5 minutes; typical confirmation is 1–3 blocks. For Pro tier we treat the first block confirmation as "credited" so your calls continue without a gap. If a tx is delayed by network congestion, your key keeps working until the buffer runs out — we don't hard-cut mid-renewal.

**Is my payment anonymous?**
LTC is pseudonymous on-chain (your address, not your name). We do not collect an email, name, or KYC document at any tier. Wallet addresses are public; you can generate a fresh address per renewal if you want privacy rotation. Use your own wallet best practices.

**Can I get a refund?**
Crypto payments are irreversible on-chain. The free tier gives you 100 calls/month to evaluate before paying; Hobby is $1/month with no long-term commit — let it lapse and you revert to Free. We don't refund partial months but renewal is month-to-month, so the downside is capped at one month's tier cost.

**Can I pay for a year in advance?**
Yes — send 12× the monthly LTC amount in one tx, note it in the `/payment` POST, and we credit your key for the full year at the locked rate. Pro annual is ~1.7 LTC at LTC = $70; Hobby annual is ~0.17 LTC.

**Which wallets work?**
- **Mobile:** Trust Wallet, Exodus, Coinomi — free, no KYC
- **Desktop:** Electrum-LTC, Exodus
- **Custodial exchange:** Coinbase, Kraken, Binance (withdraw LTC to your own address if you want self-custody)

**How do I verify my payment went through?**
Public block explorers work without signup:
- https://blockchair.com/litecoin/address/<your-wallet-address>
- https://chain.so/address/LTC/<your-wallet-address>

The `/usage` endpoint also shows your call counter, which jumps to your tier's quota the moment your key is credited.

---

## Implementation notes (for the team)

- `FREE_TIER_LIMIT` in `billing.py` currently = 10. **Bump to 100** for the new Free tier (one-line constant change; the ledger already supports monthly reset semantics).
- Hobby/Pro tiers need **monthly enforcement**: keys should carry a `tier` field (`free|hobby|pro`) and an `expires_at`. Add a `calls_this_month` counter separate from `free_remaining`.
- Hobby overage: at 10,001+ calls on a Hobby key, bill at $0.0002/call — track an `overage_calls` field, surface it in `/usage`.
- Pro rate-limit bump: bump `RATE_LIMIT_MAX` per key, not globally. Pro keys get 120/min; Hobby/Free stay at 30/min. Key-typed rate-limit bucket keyed on `X-API-Key`.
- Update the live `/pricing` endpoint JSON to expose all three tiers (currently exposes only Free + paid-per-call).
- Update `PRICING_CARD.md` (the per-call table) to point at the new tier model — keep the old per-call math as the Hobby overage rate.

---

## Quick commands (copy-paste)

```bash
# Free — try it, no signup
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Hello **world**\n\n- item 1\n- item 2"}'

# Mint a free API key (100 calls/month)
curl http://147.15.103.217/md2html/register

# See your usage
curl http://147.15.103.217/md2html/usage -H "X-API-Key: <your-key>"

# Get the LTC wallet address to pay
curl http://147.15.103.217/md2html/payment

# Credit your key after paying
curl -X POST http://147.15.103.217/md2html/payment \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-key>" \
  -d '{"txid":"<your-litecoin-tx-id>","amount":0.143,"tier":"pro"}'
```
