from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
import urllib.error

import payment_claims


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class PaymentClaimVerificationTests(unittest.TestCase):
    def test_sums_only_outputs_to_configured_wallet(self):
        txid = "c" * 64
        wallet = "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
        payload = {
            "hash": txid,
            "confirmations": 3,
            "outputs": [
                {"addresses": [wallet], "value": 60_000},
                {"addresses": ["Lother"], "value": 999_999},
                {"addresses": [wallet], "value": 40_000},
            ],
        }
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(payload)):
            verified = payment_claims.verify_ltc_transaction(txid, wallet)

        self.assertEqual(verified["txid"], txid)
        self.assertEqual(verified["value_satoshis"], 100_000)
        self.assertEqual(verified["confirmations"], 3)

    def test_rejects_mismatched_transaction_hash(self):
        txid = "d" * 64
        payload = {"hash": "e" * 64, "confirmations": 2, "outputs": []}
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(payload)):
            with self.assertRaises(payment_claims.VerificationError) as raised:
                payment_claims.verify_ltc_transaction(txid, "Lwallet")
        self.assertEqual(raised.exception.status, 502)

    def test_maps_not_found_without_leaking_provider_body(self):
        txid = "f" * 64
        error = urllib.error.HTTPError("url", 404, "not found", {}, io.BytesIO(b"provider detail"))
        with patch("payment_claims.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(payment_claims.VerificationError) as raised:
                payment_claims.verify_ltc_transaction(txid, "Lwallet")
        self.assertEqual(raised.exception.status, 404)
        self.assertEqual(raised.exception.message, "Litecoin transaction not found")


if __name__ == "__main__":
    unittest.main()
