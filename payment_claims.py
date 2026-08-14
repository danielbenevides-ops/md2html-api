"""Read-only Litecoin transaction verification for prepaid API credits."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

BLOCKCYPHER_TX_URL = "https://api.blockcypher.com/v1/ltc/main/txs/{txid}"
HTTP_TIMEOUT = 15
USER_AGENT = "md2html-payment-claim/1.0"


class VerificationError(Exception):
    """A safe-to-return payment verification failure."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def verify_ltc_transaction(txid: str, wallet_address: str) -> dict:
    """Return confirmed value sent to ``wallet_address`` by a Litecoin txid.

    This function never uses wallet private keys. It validates the response hash
    and sums only outputs explicitly paying the configured public address.
    """
    txid = str(txid or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", txid):
        raise VerificationError(400, "Invalid Litecoin transaction id")

    request = urllib.request.Request(
        BLOCKCYPHER_TX_URL.format(txid=txid),
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise VerificationError(404, "Litecoin transaction not found") from exc
        raise VerificationError(502, "Blockchain verifier returned an error") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise VerificationError(502, "Blockchain verifier is temporarily unavailable") from exc

    if str(payload.get("hash", "")).lower() != txid:
        raise VerificationError(502, "Blockchain verifier returned a mismatched transaction")

    value_satoshis = 0
    for output in payload.get("outputs", []) or []:
        addresses = output.get("addresses", []) or []
        if wallet_address in addresses:
            try:
                value_satoshis += max(int(output.get("value", 0)), 0)
            except (TypeError, ValueError):
                continue

    if value_satoshis <= 0:
        raise VerificationError(400, "Transaction does not pay the configured wallet")

    return {
        "txid": txid,
        "value_satoshis": value_satoshis,
        "confirmations": max(int(payload.get("confirmations", 0) or 0), 0),
    }
