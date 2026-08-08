#!/usr/bin/env python3
"""
check_balance.py — Query free Litecoin blockchain APIs for the balance
and transaction history of the LTC address in wallet.json.

Uses NO private keys — only the public address. Tries blockchair.com and
blockcypher.com in sequence as free public read-only endpoints.

Usage:  python check_balance.py
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

WALLET_FILE = Path(__file__).resolve().parent / "wallet.json"


def load_address() -> str:
    """Read only the public address from wallet.json. Never touches keys."""
    with WALLET_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    addr = data.get("address", "")
    if not addr:
        sys.exit("[✗] No 'address' field in wallet.json")
    return addr


def is_likely_mainnet_p2pkh(addr: str) -> bool:
    """Litecoin mainnet P2PKH addresses start with 'L' or 'M' and are ~34 chars."""
    if not addr:
        return False
    return (addr[0] in ("L", "M")) and 26 <= len(addr) <= 35 and addr.isalnum()


def get_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ltc-balance-check/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_blockchair(addr: str) -> dict | None:
    """
    Blockchair: https://api.blockchair.com/litecoin/dashboards/address/<addr>
    Returns balance in satoshi-like units; LTC = value / 1e8.
    """
    url = f"https://api.blockchair.com/litecoin/dashboards/address/{addr}"
    try:
        d = get_json(url)
        a = d["data"][addr]["address"]
        received_total = a.get("received", 0) / 1e8      # LTC received total
        balance_sat   = a.get("balance", 0)               # current balance (sat)
        tx_count      = a.get("transaction_count", 0)
        spent_total   = a.get("spent", 0) / 1e8
        balance_ltc  = balance_sat / 1e8
        return {
            "api": "blockchair",
            "balance_ltc": balance_ltc,
            "received_total_ltc": received_total,
            "spent_total_ltc": spent_total,
            "tx_count": tx_count,
        }
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as e:
        print(f"  [blockchair] failed: {e}", file=sys.stderr)
        return None


def query_blockcypher(addr: str) -> dict | None:
    """
    BlockCypher: https://api.blockcypher.com/v1/ltc/main/addrs/<addr>/balance
    Returns balance, total_received, total_sent in satoshi; LTC = value / 1e8.
    """
    url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{addr}/balance"
    try:
        d = get_json(url)
        return {
            "api": "blockcypher",
            "balance_ltc": d.get("balance", 0) / 1e8,
            "received_total_ltc": d.get("total_received", 0) / 1e8,
            "spent_total_ltc": d.get("total_sent", 0) / 1e8,
            "tx_count": d.get("n_tx", 0),
        }
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as e:
        print(f"  [blockcypher] failed: {e}", file=sys.stderr)
        return None


def main() -> int:
    addr = load_address()
    print(f"LTC address : {addr}")
    if not is_likely_mainnet_p2pkh(addr):
        print("[✗] Address does NOT look like a valid Litecoin mainnet P2PKH address.", file=sys.stderr)
        return 1
    print("[✓] Address looks like a valid Litecoin mainnet P2PKH address (starts with 'L').")
    print("-" * 50)

    # Try APIs in order; report first success, also try the fallback if first fails.
    result = None
    for query in (query_blockchair, query_blockcypher):
        print(f"Querying {query.__name__} ...")
        result = query(addr)
        if result is not None:
            break

    if result is None:
        print("[✗] All API queries failed (network/rate-limit). Check connectivity and retry.", file=sys.stderr)
        return 2

    print(f"API used     : {result['api']}")
    print(f"Balance      : {result['balance_ltc']:.8f} LTC")
    print(f"Received tot : {result['received_total_ltc']:.8f} LTC")
    print(f"Spent tot    : {result['spent_total_ltc']:.8f} LTC")
    print(f"Tx count     : {result['tx_count']}")
    print("-" * 50)
    if result['balance_ltc'] == 0 and result['received_total_ltc'] == 0:
        print("[RESULT] No LTC has been received yet. Balance is 0.")
    elif result['balance_ltc'] == 0 and result['received_total_ltc'] > 0:
        print("[RESULT] Funds were received in the past but have been spent (balance 0).")
    else:
        print(f"[RESULT] Non-zero balance: {result['balance_ltc']:.8f} LTC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
