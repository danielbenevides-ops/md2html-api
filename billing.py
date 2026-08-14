#!/usr/bin/env python3
"""Billing middleware: tracks API calls, enforces free tier, returns 402 on overage.

Clients are identified by an opaque "client id" — either the caller's IP address
(legacy behaviour, no auth required) or an API key obtained via /register and
sent in the X-API-Key header. Either way, the identifier is the key under which
usage is recorded in usage.json.

Backward compatible: record_call(ip) / check_usage(ip) still work exactly as
before when no API key is supplied. The server is free to pass an API key in
place of the IP to get a per-key bucket instead of a per-IP bucket.
"""

import ipaddress
import json
import os
import secrets
import threading
import time

USAGE_FILE = "usage.json"
FREE_TIER_LIMIT = 10
_DEFAULT_WALLET = "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
_WALLET_PUBLIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallet_public.json")


def _load_wallet_address():
    """Load only the public LTC address; private wallet material is never needed."""
    address = os.environ.get("LTC_WALLET_ADDRESS", "").strip()
    if not address:
        try:
            with open(_WALLET_PUBLIC_FILE, "r", encoding="utf-8") as wallet_file:
                address = str(json.load(wallet_file).get("address", "")).strip()
        except (OSError, ValueError, TypeError):
            address = ""
    if not (26 <= len(address) <= 35 and address[:1] in {"L", "M"} and address.isalnum()):
        address = _DEFAULT_WALLET
    return address


CRYPTO_WALLET = _load_wallet_address()

# Prefix for keys minted by /register. Only registered keys with this prefix
# are accepted as API keys; other identifiers must be valid client IPs.
KEY_PREFIX = "mk_"
_USAGE_LOCK = threading.RLock()


def _load_usage():
    """Load usage data from JSON file."""
    with _USAGE_LOCK:
        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}


def _save_usage(data):
    """Save usage data to JSON file."""
    with _USAGE_LOCK:
        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)


def generate_api_key():
    """Mint a new opaque API key (32 hex chars, url-safe)."""
    return KEY_PREFIX + secrets.token_hex(16)


def is_valid_api_key(api_key, data=None):
    """Return whether ``api_key`` is a registered, correctly-prefixed key."""
    if not isinstance(api_key, str) or not api_key.startswith(KEY_PREFIX):
        return False
    if data is None:
        data = _load_usage()
    entry = data.get(api_key)
    return isinstance(entry, dict) and entry.get("kind") == "api_key" and not entry.get("revoked")


def _is_client_ip(client_id):
    """Return whether ``client_id`` is a valid legacy IP identifier."""
    if not isinstance(client_id, str):
        return False
    try:
        ipaddress.ip_address(client_id)
        return True
    except ValueError:
        return False


def register_client(ip=None):
    """Generate a fresh API key, persist a zero-count usage entry for it, and
    return the key plus the initial entry.

    The optional ``ip`` is recorded on the entry for bookkeeping (so an operator
    can later see which address first minted a key); it does NOT affect the free
    tier, which is keyed on the API key, not the IP.
    """
    with _USAGE_LOCK:
        key = generate_api_key()
        if not isinstance(key, str) or not key.startswith(KEY_PREFIX):
            raise RuntimeError("generated API key has an invalid prefix")
        now = int(time.time())
        data = _load_usage()
        data[key] = {
            "call_count": 0,
            "first_call": now,
            "last_call": now,
            "kind": "api_key",
            "ip": ip,
        }
        _save_usage(data)
        return {
            "api_key": key,
            "wallet_address": CRYPTO_WALLET,
            "free_tier_limit": FREE_TIER_LIMIT,
            "calls_made": 0,
            "remaining": FREE_TIER_LIMIT,
        }


def record_call(api_key):
    """Increment call count for a registered API key or client IP.

    Unknown/spoofed API keys are rejected instead of being auto-registered.
    Returns usage info, a 401 for invalid identifiers, or a 402 on overage.
    """
    with _USAGE_LOCK:
        data = _load_usage()
        if isinstance(api_key, str):
            api_key = api_key.strip()
        if not (is_valid_api_key(api_key, data) or _is_client_ip(api_key)):
            return {
                "status": 401,
                "error": "Invalid API key",
                "message": "Use an API key issued by /register (mk_...) or omit it.",
            }

        now = int(time.time())
        if api_key not in data:
            data[api_key] = {"call_count": 0, "first_call": now, "last_call": now}

        entry = data[api_key]
        entry["call_count"] += 1
        entry["last_call"] = now
        _save_usage(data)

        count = entry["call_count"]
        remaining = FREE_TIER_LIMIT - count

        if count > FREE_TIER_LIMIT:
            return {
                "status": 402,
                "error": "Payment Required",
                "message": (
                    f"Free tier limit ({FREE_TIER_LIMIT} calls) exceeded. "
                    f"You made {count} calls. Send payment to continue."
                ),
                "wallet_address": CRYPTO_WALLET,
                "calls_made": count,
                "free_tier_limit": FREE_TIER_LIMIT,
            }

        return {
            "status": 200,
            "calls_made": count,
            "remaining": max(remaining, 0),
            "free_tier_limit": FREE_TIER_LIMIT,
        }


def check_usage(api_key):
    """Return current usage for a client without incrementing."""
    with _USAGE_LOCK:
        data = _load_usage()
        return data.get(api_key, {"call_count": 0})


def reset_usage(api_key):
    """Reset usage for a client (e.g., after payment confirmed)."""
    with _USAGE_LOCK:
        data = _load_usage()
        if api_key in data:
            data[api_key]["call_count"] = 0
            _save_usage(data)
    return True


if __name__ == "__main__":
    # --- Simple test ---
    test_key = "127.0.0.1"
    test_usage_file = "usage.json"

    # Clean slate
    if os.path.exists(test_usage_file):
        os.remove(test_usage_file)

    print("=== Billing Middleware Test ===")
    print(f"Free tier: {FREE_TIER_LIMIT} calls")
    print(f"Wallet:    {CRYPTO_WALLET}\n")

    # 1) Register a brand-new API key
    reg = register_client(ip="127.0.0.1")
    print(f"Registered new API key: {reg['api_key']}")
    print(f"  remaining: {reg['remaining']}/{reg['free_tier_limit']}\n")

    # 2) Consume the free tier using that key
    for i in range(FREE_TIER_LIMIT):
        result = record_call(reg["api_key"])
        print(f"Call {result['calls_made']:2d}: status={result['status']}, "
              f"remaining={result.get('remaining', 0)}")

    # This call should trigger 402
    print()
    result = record_call(reg["api_key"])
    print(f"Call {result['calls_made']}: status={result['status']}, error={result.get('error', 'N/A')}")
    if result["status"] == 402:
        print(f"  -> Payment Required! Wallet: {result['wallet_address']}")
        print(f"  -> Message: {result['message']}")

    print(f"\nFinal usage: {check_usage(reg['api_key'])}")

    # Cleanup test artifacts
    if os.path.exists(test_usage_file):
        os.remove(test_usage_file)
    print("\nTest complete. usage.json cleaned up.")
