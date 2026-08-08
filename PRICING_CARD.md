# Pricing Card

## API Call Pricing

### Free Tier
- **10 calls** free (no payment required)

### Paid Tier
- **$0.001 per call** (one-tenth of a cent)
- LTC equivalent: **~0.00001429 LTC / call** (at LTC = $70)
  - Calculation: $0.001 ÷ $70 = 0.00001429 LTC

### Minimum Viable Payment
- Smallest practical LTC transaction: **~0.0001 LTC** (~$0.007)
- This buys approximately **7 calls**
- Below this amount, transaction fees make micropayments impractical

---

## LTC Amount → Call Count Table
*(Based on $0.001/call and LTC = $70)*

| LTC Amount | USD Value | Calls Purchased |
|------------|-----------|-----------------|
| 0.0001 LTC | $0.007    | ~7 calls        |
| 0.0005 LTC | $0.035    | ~35 calls       |
| 0.001 LTC  | $0.070    | ~70 calls       |
| 0.005 LTC  | $0.35     | ~350 calls      |
| 0.01 LTC   | $0.70     | ~700 calls      |
| 0.05 LTC   | $3.50     | ~3,500 calls    |
| 0.1 LTC    | $7.00     | ~7,000 calls    |
| 0.5 LTC    | $35.00    | ~35,000 calls   |
| 1.0 LTC    | $70.00    | ~70,000 calls   |

---

## Wallet

- **Address:** `La...` (Litecoin mainnet P2PKH)
- **Balance (verified):** 0.00000000 LTC — *no payments received yet*

## Notes

- Call counts are approximate (rounded down for practicality).
- Pricing scales linearly; no bulk discount at this tier.
- LTC price is volatile — the calls-per-LTC ratio updates with market price. Recalculate as: `calls = LTC_amount × LTC_price_USD ÷ 0.001`.
- Free tier calls do not carry over and are intended for trial/evaluation use.
