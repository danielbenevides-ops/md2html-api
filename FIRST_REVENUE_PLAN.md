# First Revenue Plan — MD2HTML API

**Goal:** receive the first legitimate on-chain payment of at least **0.001 LTC** without paid acquisition, spam, or unsupported claims.

## Baseline

- Real revenue: **0 LTC**.
- Confirmed paying users: **0**.
- Public source: <https://github.com/danielbenevides-ops/md2html-api>.
- Hosted API: <http://147.15.103.217/md2html/>.
- Offer: 10 free billable calls, then **0.001 LTC for 100 prepaid calls**.
- Payment path: register key → send LTC → wait for 1 confirmation → `POST /payment/claim` → verify `/usage`.

## Funnel and measurements

| Stage | Observable signal | Target for first cycle |
|---|---|---:|
| Discovery | GitHub traffic/referrers and landing requests | 50 visits |
| Activation | `/register` 200 responses | 10 keys |
| Value | successful billable endpoint calls | 5 activated keys |
| Paywall intent | `402` responses | 3 clients |
| Payment attempt | `/payment/claim` responses other than 401/400 | 1 |
| Revenue | confirmed claim and wallet received value | ≥0.001 LTC |

Do not infer users or revenue from raw calls. A payment counts only when the blockchain output, claim record, and wallet received value agree.

## Experiments, ordered by cost and reversibility

1. **GitHub-native discovery — started**
   - Public repo, homepage, license, topics, CI, Discussions, and tagged release.
   - CTA: run the free example; ask for concrete endpoint feedback.
   - Success: first non-owner star, issue, discussion, or API key registration.

2. **Developer-directory submission — after HTTPS**
   - Submit one accurate PR to a maintained public-API directory.
   - Do not duplicate submissions or claim acceptance before merge.
   - Blocker: public endpoint currently uses HTTP; obtain a free HTTPS hostname/certificate first.

3. **One honest launch post per authenticated community**
   - Use the prepared HN/Dev.to/Reddit drafts only after refreshing version and pricing.
   - Ask for technical feedback, not votes; never cross-post simultaneously.
   - Record the canonical URL only after it is publicly reachable.

4. **Opt-in outreach only**
   - Respond only where a developer explicitly asks for hosted Markdown conversion or a tiny utility API.
   - Maximum five individualized messages per week; no scraped lists or bulk DMs.

## Product safeguards

- Txid must be 64 hex characters, confirmed, and pay the configured wallet.
- One txid can fund only one API key; same-key retries are idempotent.
- Key rotation preserves call count, paid credits, and payment claims.
- The server never reads or deploys private wallet material.
- No real-money spend without a separate explicit budget decision.

## Daily 5-minute review

1. Check `/health`, `/stats`, `/pricing`, and wallet balance.
2. Compare claim count against on-chain received transactions.
3. Record only changed metrics in `ledger.json`.
4. If visits exist but registrations do not, simplify onboarding.
5. If registrations and 402s exist but claims do not, improve payment instructions before adding traffic.
