# Payments: Free Crypto Micro-Payment Setup

This document explains how the autonomous-business-product receives
micro-payments with **NO KYC, NO paid service, NO third-party custody**.

## TL;DR

1. Run `python generate_wallet.py` to generate a **Litecoin (LTC)** address.
2. Copy the printed `LTC address` (starts with `L` or `M`).
3. Paste it into your landing page's payment box (snippet is printed too).
4. Users send LTC directly on-chain to that address. You hold the keys.

## Why Litecoin (LTC)?

- Very low fees (a few cents) — ideal for micro-payments.
- Established, widely supported by free wallets (Trust Wallet, Exodus, Electrum-LTC).
- Same cryptography as Bitcoin, well-understood.
- Deriving an LTC address is a pure-Python one-liner using `ecdsa` + `base58`.

## How the wallet is generated

`generate_wallet.py` does NOT call any API. It:

1. Generates a 256-bit private key on the **secp256k1** curve (`ecdsa`).
2. Computes the uncompressed public key (65 bytes, `0x04` prefix).
3. Applies **SHA256 → RIPEMD160** (Bitcoin's "Hash160").
4. Base58Check-encodes with Litecoin's mainnet version byte `0x30` → `L…` address.

Dependencies (small, pure-Python, free):

```bash
pip install ecdsa base58
```

Run it:

```bash
cd C:\Users\pqcai\autonomous-business-product
python generate_wallet.py
```

Output:

- Prints the **LTC address** (safe to share) and the **private key** (SECRET).
- Saves everything to `wallet.json` (chmod 600).

## SECURITY — read this

- **NEVER** commit `wallet.json` to git. It contains the private key.
- Back up `wallet.json` somewhere safe and offline. Losing it = losing funds.
- The **address** is public; the **private key** (WIF / hex) controls the funds.
- Anyone with the private key can spend the LTC.

## Verifying funds (no paid service)

Free option: paste the LTC address into a public blockchain explorer.

- https://chain.so/address/LTC/<your-address>
- https://blockchair.com/litecoin/address/<your-address>

These show incoming transactions and balance without any signup.

## Recovering / spending funds later

Import the WIF private key (from `wallet.json`) into any free Litecoin wallet:

- **Electrum-LTC** (desktop): *File → New/Restore → Import private key*.
- **Trust Wallet** / **Exodus** (mobile): create wallet, then use
  "Import private key" (Exodus supports this via their desktop DeFi integrations).
- **Coinomi** (mobile): *Add wallet → Litecoin → Advanced → Import WIF*.

Always test with a tiny amount first (e.g. 0.001 LTC) before relying on it.

## Alternative: manual wallet on a free platform

If you prefer not to generate keys via script, install a free wallet app,
create a LTC wallet, and copy its receive address:

1. **Trust Wallet** (mobile, iOS/Android) — free, no KYC, in-app LTC wallet.
2. **Exodus** (desktop + mobile) — free, no KYC, visually nice.
3. **Electrum-LTC** (desktop, lightweight) — free, no KYC, advanced.

In each app: *Create new wallet → Litecoin → Receive → Copy address*.
Paste that address into your landing page exactly as shown.

---

**Important**: Treat the script's printed `wallet.json` like cash. There is no
"password reset" on a blockchain — whoever holds the private key holds the LTC.
