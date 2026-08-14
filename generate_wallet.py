#!/usr/bin/env python3
"""
generate_wallet.py — Generate a simple Litecoin (LTC) wallet address
for receiving micro-payments. NO KYC, NO paid service, NO external API.

Litecoin uses the same secp256k1 curve as Bitcoin but with a different
version byte (0x30 for mainnet P2PKH addresses), so addresses start with
"L" or "M".

Flow: secp256k1 privkey -> pubkey -> SHA256+RIPEMD160 -> base58check.

Dependencies (small, pure-python, free):
    pip install ecdsa base58

Output: LTC address + private key (WIF). The address is safe to display
publicly on a landing page so anyone can send LTC micro-payments.
KEEP THE PRIVATE KEY SECRET — it controls the funds.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def _ensure_deps() -> None:
    """Best-effort auto-install of the small pure-Python deps on first run."""
    try:
        import ecdsa  # noqa: F401
        import base58  # noqa: F401
        return
    except ImportError:
        pass
    print("[!] Missing dependencies (ecdsa / base58). Attempting auto-install…", file=sys.stderr)
    # Try the current interpreter's pip, then fall back to a system pip.
    for cmd in (
        [sys.executable, "-m", "pip", "install", "ecdsa", "base58"],
        ["pip", "install", "ecdsa", "base58"],
    ):
        try:
            subprocess.check_call(cmd)
            import ecdsa  # noqa: F401
            import base58  # noqa: F401
            print("[✓] Dependencies installed.", file=sys.stderr)
            return
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    sys.exit(
        "[✗] Could not install ecdsa/base58 automatically.\n"
        "    Run this once manually:  pip install ecdsa base58\n"
        "    (or use the Python that has pip), then re-run this script."
    )


_ensure_deps()

# secp256k1 curve parameters (same as Bitcoin/Litecoin)
from ecdsa import SigningKey, SECP256k1
import base58

# Litecoin mainnet P2PKH version byte
LTC_VERSION_BYTE = 0x30


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def ripemd160(b: bytes) -> bytes:
    # RIPEMD160 is available via hashlib.new in modern Python
    return hashlib.new("ripemd160", b).digest()


def hash160(b: bytes) -> bytes:
    """Bitcoin/Litecoin 'Hash160': SHA256 then RIPEMD160."""
    return ripemd160(sha256(b))


def base58check(version_byte: int, payload: bytes) -> str:
    """Base58Check encode: version || payload || first4(sha256(sha256(...)))."""
    data = bytes([version_byte]) + payload
    checksum = sha256(sha256(data))[:4]
    return base58.b58encode(data + checksum).decode("ascii")


def generate_keypair() -> tuple[str, str, str]:
    """
    Generate a fresh Litecoin keypair.
    Returns: (private_key_wif, private_key_hex, ltc_address)
    """
    # 1. Private key: 32 random bytes (256-bit) on secp256k1
    sk = SigningKey.generate(curve=SECP256k1)
    priv_hex = sk.to_string().hex()

    # 2. Public key: uncompressed, prefixed with 0x04
    vk = sk.get_verifying_key()
    pub_bytes = b"\x04" + vk.to_string()  # 65 bytes uncompressed

    # 3. pubkey -> hash160 (20-byte 'hash160')
    h160 = hash160(pub_bytes)

    # 4. base58check with Litecoin mainnet version byte 0x30 -> "L..." address
    address = base58check(LTC_VERSION_BYTE, h160)

    # 5. Private key in WIF (Wallet Import Format), Litecoin mainnet prefix 0xB0
    #    (uncompressed, no compression flag appended)
    wif = base58check(0xB0, sk.to_string())

    return wif, priv_hex, address


def save_wallet(wif: str, priv_hex: str, address: str, out_dir: Path) -> Path:
    """Save wallet details to a JSON file. The private key file MUST stay private."""
    out_dir.mkdir(parents=True, exist_ok=True)
    wallet = {
        "network": "litecoin-mainnet",
        "address": address,
        "private_key_wif": wif,
        "private_key_hex": priv_hex,
        "note": (
            "Share the 'address' publicly to receive LTC micro-payments. "
            "NEVER share/export the private key. Back this file up securely; "
            "losing the private key means losing all funds."
        ),
    }
    keyfile = out_dir / "wallet.json"
    # Restrict permissions on the key file where possible (POSIX)
    fd = os.open(str(keyfile), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(wallet, f, indent=2)
    try:
        os.chmod(str(keyfile), 0o600)
    except OSError:
        pass  # chmod no-op on Windows for this attribute
    return keyfile


def print_landing_snippet(address: str) -> None:
    """Print an HTML snippet showing the address on a landing page."""
    snippet = (
        f"""
<div class="payment-box">
  <h3>Support us with a micro-payment</h3>
  <p>Send any amount of Litecoin (LTC) to:</p>
  <code class="ltc-address">{address}</code>
  <p>No signup, no middleman — direct on-chain.</p>
</div>
"""
    )
    print("\n--- Landing page HTML snippet ---")
    print(snippet)


def main() -> int:
    out_dir = Path(__file__).resolve().parent

    wif, priv_hex, address = generate_keypair()
    keyfile = save_wallet(wif, priv_hex, address, out_dir)

    print("=" * 60)
    print("  LITECOIN WALLET GENERATED")
    print("=" * 60)
    print(f"LTC address (SAFE to share) : {address}")
    print("Private key material         : saved only in wallet.json (not printed)")
    print("-" * 60)
    print(f"Wallet details saved to      : {keyfile}")
    print(f"  (chmod 600 — keep this file private!)")
    print("=" * 60)
    print("\nNEXT: display the LTC address on your landing page.")
    print_landing_snippet(address)
    return 0


if __name__ == "__main__":
    sys.exit(main())
