#!/usr/bin/env python3
"""
check_payments.py — Verify incoming LTC micro-payments on the MD2HTML API
business wallet and credit the client's account.

1. Query BlockCypher's free LTC mainnet API for the wallet's full transaction
   history (read-only — no private keys used).
2. Walk every confirmed incoming transaction; for any output paying our address
   that we have not already processed, convert the LTC amount to API-call credit
   and apply it to usage.json under the configured payer account.
3. Append a record row for every transaction seen (duplicates skipped) to
   transactions.json so each payment is auditable.
4. Print a human-readable summary (balance, tx count, credits applied, errors).

Pricing model (from billing.py / PAYMENTS.md):
  - Free tier : 10 calls per client, then 402 Payment Required.
  - Paid calls: $0.001 / call, settled in LTC.

BlockCypher returns values in satoshi (1 LTC = 100_000_000 sat). We convert to
LTC, then to a USD value using an optional price hook, then to call credits at
the posted $0.001/call rate. A flat fallback price of $1 USD = 1 LTC is used if
no price source is available, so credits are at minimum 1:1 LTC-to-calls when the
price lookup fails — adjust PRICE_FALLBACK_USD_PER_LTC below to tighten this.

Usage:
    python check_payments.py                 # normal run
    python check_payments.py --dry-run        # show what would change, write nothing
    python check_payments.py --account KEY    # credit a specific usage.json key
                                               # (default: a synthetic "ltc_payer" key)

Exit codes:
    0  success (whether or not payments were found)
    1  usage error / bad args
    2  could not reach any blockchain API after all retries/fallbacks
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
WALLET_ADDR = "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"          # LTC mainnet
USAGE_FILE = BASE_DIR / "usage.json"
TXLOG_FILE = BASE_DIR / "transactions.json"
STATE_FILE = BASE_DIR / ".payments_state.json"               # tracks processed tx ids

# Pricing ------------------------------------------------------------ {{{{{
# $0.001 per API call. To convert an LTC amount to call credits we need a
# USD/LTC price. We try a free Coinbase API; if it fails we fall back to a
# conservative constant so the script never silently skips a credit.
USD_PER_CALL = 0.001
PRICE_FALLBACK_USD_PER_LTC = 70.0   # conservative, update as needed
# }}}}}

# BlockCypher endpoints ------------------------------------------------ {{{{{
BC_FULL_URL = (
    "https://api.blockcypher.com/v1/ltc/main/addrs/{addr}/full"
    "?limit=50&txlimit=50"            # last 50 txs, 50 outputs each
)
BC_BALANCE_URL = "https://api.blockcypher.com/v1/ltc/main/addrs/{addr}/balance"
# }}}}}

HTTP_TIMEOUT = 25
USER_AGENT = "md2html-payment-checker/1.0"
PROCESSED_KEY = "processed_txids"


# -------------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------------

def log(msg: str) -> None:
    """Timestamped stderr/stdout line."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def http_get_json(url: str, timeout: int = HTTP_TIMEOUT) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def fetch_ltc_usd_price() -> float:
    """Best-effort spot price from Coinbase public API. Falls back on error."""
    url = ("https://api.coinbase.com/v2/prices/LTC-USD/spot")
    try:
        d = http_get_json(url, timeout=10)
        return float(d["data"]["amount"])
    except Exception as e:  # network/parse/rate-limit
        log(f"  price lookup failed ({e!r}); using fallback "
            f"USD/LTC={PRICE_FALLBACK_USD_PER_LTC}")
        return PRICE_FALLBACK_USD_PER_LTC


# -------------------------------------------------------------------------
# JSON persistence (atomic-ish writes, missing files created)
# -------------------------------------------------------------------------

def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log(f"  ! could not parse {path.name} ({e}); starting fresh")
        return default


def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)          # atomic on same filesystem


# -------------------------------------------------------------------------
# Blockchain query
# -------------------------------------------------------------------------

def query_wallet(addr: str) -> dict | None:
    """
    Return a normalized wallet snapshot:
      {
        "balance_ltc": float,
        "total_received_ltc": float,
        "n_tx": int,
        "incoming": [ {txid, ts, value_ltc, confirmations}, ... ],
      }
    Pulls the full tx list and filters to outputs paying `addr`.
    """
    url = BC_FULL_URL.format(addr=addr)
    try:
        d = http_get_json(url)
    except Exception as e:
        log(f"  ! blockcypher full fetch failed: {e!r}")
        # Fallback: at least get the balance summary so we can print it.
        try:
            b = http_get_json(BC_BALANCE_URL.format(addr=addr))
            return {
                "balance_ltc": b.get("balance", 0) / 1e8,
                "total_received_ltc": b.get("total_received", 0) / 1e8,
                "n_tx": b.get("n_tx", 0),
                "incoming": [],
                "_balance_fallback": True,
            }
        except Exception as e2:
            log(f"  ! blockcypher balance fallback also failed: {e2!r}")
            return None

    incoming = []
    for tx in d.get("txs", []) or []:
        txid = tx.get("hash", "")
        # confirmation / time
        confirmations = tx.get("confirmations", 0) or 0
        block_time = tx.get("block_time") or tx.get("received") or tx.get("confirmed")
        # BlockCypher "block_time"/"received" are unix seconds; "confirmed" is
        # an ISO string. Normalise to integer epoch.
        if isinstance(block_time, str):
            try:
                ts = int(datetime.fromisoformat(
                    block_time.replace("Z", "+00:00")).timestamp())
            except Exception:
                ts = int(time.time())
        else:
            ts = int(block_time or time.time())

        # Sum outputs whose addresses include ours (that's money TO us).
        value_sat = 0
        for out in tx.get("outputs", []) or []:
            if WALLET_ADDR in (out.get("addresses", []) or []):
                value_sat += int(out.get("value", 0) or 0)

        # A tx can also have inputs spending our coins (an outgoing spend).
        # If we received net positive, treat it as an incoming payment; if it
        # only spends, skip it (value_sat stays 0).
        if value_sat > 0:
            incoming.append({
                "txid": txid,
                "ts": ts,
                "value_ltc": value_sat / 1e8,
                "confirmations": confirmations,
            })

    return {
        "balance_ltc": d.get("balance", 0) / 1e8,
        "total_received_ltc": d.get("total_received", 0) / 1e8,
        "n_tx": d.get("n_tx", 0),
        "incoming": incoming,
        "_balance_fallback": False,
    }


# -------------------------------------------------------------------------
# Credit application
# -------------------------------------------------------------------------

def load_state() -> dict:
    return load_json(STATE_FILE, {PROCESSED_KEY: []})


def already_processed(state: dict, txid: str) -> bool:
    return txid in set(state.get(PROCESSED_KEY, []))


def apply_credit(account_key: str, ltc_amount: float,
                 usd_per_ltc: float, dry_run: bool) -> dict:
    """
    Convert `ltc_amount` to call credits and add them to the account entry in
    usage.json. Returns a dict describing what happened.

    The credit is stored under "purchased_calls" (additive) on the existing
    usage entry for `account_key`; if the entry doesn't exist it is created.
    """
    usd_value = ltc_amount * usd_per_ltc
    calls = int(usd_value / USD_PER_CALL)        # truncate fractional cents
    if calls <= 0:
        return {
            "account": account_key, "ltc": ltc_amount, "usd_value": usd_value,
            "calls_credited": 0, "note": "amount too small for a credit",
        }

    if dry_run:
        log(f"  [dry-run] would credit {calls} calls "
            f"(LTC={ltc_amount:.8f}, USD≈{usd_value:.4f}) to '{account_key}'")
        return {"account": account_key, "ltc": ltc_amount,
                "usd_value": usd_value, "calls_credited": calls, "dry_run": True}

    usage = load_json(USAGE_FILE, {})
    now = int(time.time())
    entry = usage.get(account_key)
    if not entry:
        entry = {"call_count": 0, "first_call": now, "last_call": now}
        usage[account_key] = entry

    # Track purchased (prepaid) credits separately from the free-tier count so
    # billing.py's 10-free-call logic still works. billing.py reads call_count
    # and FREE_TIER_LIMIT; purchased_calls is the topped-up pool it will draw
    # from once the free tier is exhausted (see __init__/billing integration).
    entry["purchased_calls"] = int(entry.get("purchased_calls", 0)) + calls
    entry["last_credit_ts"] = now
    entry["last_credit_ltc"] = round(ltc_amount, 8)
    entry["last_credit_calls"] = calls
    save_json(USAGE_FILE, usage)

    log(f"  + credited {calls} calls to '{account_key}' "
        f"(LTC={ltc_amount:.8f}, USD≈{usd_value:.4f})")
    return {"account": account_key, "ltc": ltc_amount,
            "usd_value": usd_value, "calls_credited": calls}


# -------------------------------------------------------------------------
# Transaction log (auditable history of every tx we ever saw)
# -------------------------------------------------------------------------

def append_txlog(records: list[dict]) -> None:
    """Append new tx records (already deduped) to transactions.json.

    Always (re)writes the file so `last_checked` advances even when no new
    records arrive — keeps an auditable heartbeat.
    """
    txlog = load_json(TXLOG_FILE, {"transactions": []})
    # Defensive: support a bare list or the documented {"transactions":[...]}.
    if isinstance(txlog, list):
        txlog = {"transactions": txlog}
    if "transactions" not in txlog:
        txlog["transactions"] = []
    txlog["transactions"].extend(records)
    txlog["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_json(TXLOG_FILE, txlog)


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Check LTC wallet for new payments.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would change without writing files.")
    ap.add_argument("--account", default="ltc_payer",
                    help="usage.json key to credit (default: 'ltc_payer').")
    ap.add_argument("--confirm-only", action="store_true",
                    help="Only credit transactions with >=1 confirmation.")
    args = ap.parse_args()

    log(f"MD2HTML payment checker — wallet {WALLET_ADDR}")
    log(f"account='{args.account}'  dry_run={args.dry_run}  "
        f"confirm_only={args.confirm_only}")

    # 1) Hit the blockchain
    snap = query_wallet(WALLET_ADDR)
    if snap is None:
        log("FATAL: could not reach any blockchain API.")
        return 2

    if snap.get("_balance_fallback"):
        log("  (balance-only fallback — tx details unavailable this run)")

    log(f"Wallet balance : {snap['balance_ltc']:.8f} LTC")
    log(f"Total received : {snap['total_received_ltc']:.8f} LTC "
        f"({snap['n_tx']} on-chain txs)")
    log(f"Incoming outputs seen this pull: {len(snap['incoming'])}")

    # Nothing further to do if there are no incoming outputs.
    if not snap["incoming"]:
        log("No incoming payments to process.")
        append_txlog([])                       # still update last_checked timestamp
        _print_summary(snap, [], 0)
        return 0

    # 2) Dedupe against previously-processed txids
    state = load_state()
    processed = set(state.get(PROCESSED_KEY, []))
    usd_per_ltc = fetch_ltc_usd_price()
    log(f"Spot LTC/USD ≈ {usd_per_ltc:.2f}  (rate ${USD_PER_CALL}/call)")

    new_records: list[dict] = []
    total_calls = 0
    new_txids: list[str] = []

    for inc in snap["incoming"]:
        txid = inc["txid"]
        if txid in processed:
            continue                          # already credited on a prior run
        if args.confirm_only and inc["confirmations"] < 1:
            log(f"  · skipping unconfirmed tx {txid[:16]}… ({inc['confirmations']} conf)")
            continue

        # Build auditable record
        rec = {
            "txid": txid,
            "address": WALLET_ADDR,
            "ts": inc["ts"],
            "ts_iso": datetime.fromtimestamp(inc["ts"], tz=timezone.utc).isoformat(),
            "value_ltc": inc["value_ltc"],
            "confirmations": inc["confirmations"],
            "credited_account": args.account,
            "usd_value_at_credit": round(inc["value_ltc"] * usd_per_ltc, 6),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        result = apply_credit(args.account, inc["value_ltc"], usd_per_ltc,
                              dry_run=args.dry_run)
        rec["calls_credited"] = result.get("calls_credited", 0)
        rec["dry_run"] = bool(args.dry_run)
        total_calls += rec["calls_credited"]

        new_records.append(rec)
        new_txids.append(txid)

    # 3) Persist state + txlog atomically (skip state writes in dry-run)
    if new_txids and not args.dry_run:
        processed.update(new_txids)
        state[PROCESSED_KEY] = sorted(processed)
        save_json(STATE_FILE, state)

    append_txlog(new_records) if not args.dry_run else None

    _print_summary(snap, new_records, total_calls)
    return 0


def _print_summary(snap: dict, new_records: list[dict], total_calls: int) -> None:
    print()
    print("=" * 64)
    print("  PAYMENT CHECK SUMMARY")
    print("=" * 64)
    print(f"  Wallet            : {WALLET_ADDR}")
    print(f"  On-chain balance  : {snap['balance_ltc']:.8f} LTC")
    print(f"  Total received    : {snap['total_received_ltc']:.8f} LTC")
    print(f"  On-chain tx count : {snap['n_tx']}")
    print(f"  New payments seen : {len(new_records)}")
    if new_records:
        for r in new_records:
            print(f"    - tx {r['txid'][:24]}…  "
                  f"{r['value_ltc']:.8f} LTC  → {r['calls_credited']} calls  "
                  f"({r.get('confirmations', 0)} conf)")
    print(f"  Calls credited    : {total_calls}")
    print("=" * 64)

    # Show current usage.json state for the default account too
    try:
        usage = load_json(USAGE_FILE, {})
        print(f"  usage.json accounts: {len(usage)}")
        for k, v in usage.items():
            cc = v.get("call_count", 0)
            pc = v.get("purchased_calls", 0)
            print(f"    · {k}: calls={cc}  purchased={pc}")
    except Exception as e:
        print(f"  (could not read usage.json: {e!r})")
    print("=" * 64)


if __name__ == "__main__":
    sys.exit(main())
